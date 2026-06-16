#!/usr/bin/env python
"""
RAG 知识库 CLI —— 零外部依赖，纯标准库 + Embedding API。

用法:
  python cli.py add <标题> <内容>
  python cli.py query <问题> [-k N]
  python cli.py delete <内容描述>
  python cli.py list
  python cli.py rebuild
  python cli.py clear
"""

import argparse
import json
import math
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_ENV_FILE = _SCRIPT_DIR / ".env"

SUFFIXES = {".md", ".txt"}
CONFIG_FILES = {"cli.py", ".env", "requirements.txt"}


def _load_env() -> dict[str, str]:
    if not _ENV_FILE.exists():
        return {}
    env = {}
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


_env = _load_env()
KB_PATH = Path(_env.get("DEFAULT_KB_PATH", str(_SCRIPT_DIR.parent)))
EMBEDDING_API_KEY = _env.get("EMBEDDING_API_KEY", "")
EMBEDDING_BASE_URL = _env.get("EMBEDDING_BASE_URL", "")
EMBEDDING_MODEL = _env.get("EMBEDDING_MODEL", "")
CHUNK_SIZE = int(_env.get("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(_env.get("CHUNK_OVERLAP", "100"))
TOP_K = int(_env.get("TOP_K", "5"))

STORAGE_DIR = KB_PATH


# ── HTTP ──────────────────────────────────────────────────

def _post(url: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {EMBEDDING_API_KEY}",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Embedding ─────────────────────────────────────────────

def _embed(texts: list[str]) -> list[list[float]]:
    url = f"{EMBEDDING_BASE_URL.rstrip('/')}/embeddings"
    resp = _post(url, {"model": EMBEDDING_MODEL, "input": texts})
    return [item["embedding"] for item in resp["data"]]


def _embed_one(text: str) -> list[float]:
    return _embed([text])[0]


# ── 分块 ──────────────────────────────────────────────────

def _chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        c = text[start:end]
        if c.strip():
            chunks.append(c)
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def _chunk_docs(documents: list[dict]) -> list[dict]:
    result = []
    for doc in documents:
        for i, c in enumerate(_chunk_text(doc["text"])):
            result.append({"source": doc["source"], "chunk_index": i, "text": c})
    return result


# ── 文档加载 ──────────────────────────────────────────────

def _load_docs() -> list[dict]:
    docs = []
    for fp in sorted(KB_PATH.rglob("*")):
        if fp.suffix.lower() not in SUFFIXES or not fp.is_file():
            continue
        if "storage" in fp.parts or fp.name in CONFIG_FILES:
            continue
        text = fp.read_text(encoding="utf-8")
        if text.strip():
            docs.append({"source": str(fp), "text": text})
    return docs


# ── 向量运算 ──────────────────────────────────────────────

def _l2(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class _Index:
    def __init__(self):
        self.vectors: list[list[float]] = []
        self.meta: list[dict] = []

    def build(self, vectors: list[list[float]], meta: list[dict]):
        self.vectors = vectors
        self.meta = meta
        self._save()

    def add(self, vectors: list[list[float]], meta: list[dict]):
        if not self.vectors and (STORAGE_DIR / "index.json").exists():
            self.load()
        self.vectors.extend(vectors)
        self.meta.extend(meta)
        self._save()

    def load(self):
        ip = STORAGE_DIR / "index.json"
        mp = STORAGE_DIR / "metadata.json"
        if not ip.exists() or not mp.exists():
            raise FileNotFoundError("索引不存在")
        self.vectors = json.loads(ip.read_text(encoding="utf-8"))
        self.meta = json.loads(mp.read_text(encoding="utf-8"))

    def _save(self):
        (STORAGE_DIR / "index.json").write_text(json.dumps(self.vectors))
        (STORAGE_DIR / "metadata.json").write_text(json.dumps(self.meta))

    def search(self, query_vec: list[float], top_k: int) -> list[dict]:
        scored = [(i, _l2(v, query_vec)) for i, v in enumerate(self.vectors)]
        scored.sort(key=lambda x: x[1])
        top = scored[:min(top_k, len(scored))]
        return [{**self.meta[i].copy(), "distance": dist} for i, dist in top]


# ═══════════════════════════════════════════════════════════
# 公开 API
# ═══════════════════════════════════════════════════════════

def add(title: str, content: str) -> dict:
    """添加一条笔记。"""
    slug = re.sub(r'[\\/:*?"<>|]', "-", title).strip()[:80]
    filepath = KB_PATH / f"{slug}.md"
    body = f"# {title}\n\n{content}\n"
    filepath.write_text(body, encoding="utf-8")

    chunks = _chunk_docs([{"source": str(filepath), "text": body}])
    texts = [c["text"] for c in chunks]
    vectors = _embed(texts)
    meta = [{"source": c["source"], "chunk_index": c["chunk_index"], "text": c["text"]} for c in chunks]

    idx = _Index()
    try:
        idx.load()
        idx.add(vectors, meta)
    except FileNotFoundError:
        idx.build(vectors, meta)

    return {"title": title, "path": str(filepath), "chunks": len(chunks)}


def query(question: str, top_k: int | None = None) -> list[dict]:
    """语义检索，返回相关原文片段。"""
    idx = _Index()
    idx.load()
    q_vec = _embed_one(question)
    return idx.search(q_vec, top_k or TOP_K)


def delete(content: str) -> dict:
    """智能删除：先检索相关chunks → 从源文件移除 → 重建索引。"""
    results = query(content, top_k=TOP_K * 2)
    if not results:
        return {"removed_chunks": 0, "affected_files": 0, "documents": 0, "chunks": 0}

    by_file: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_file[r["source"]].append(r)

    for filepath, chunks in by_file.items():
        original = Path(filepath).read_text(encoding="utf-8")
        for c in chunks:
            original = original.replace(c["text"], "")
        while "\n\n\n" in original:
            original = original.replace("\n\n\n", "\n\n")
        cleaned = original.strip()
        if cleaned:
            Path(filepath).write_text(cleaned + "\n", encoding="utf-8")
        else:
            Path(filepath).unlink()

    info = rebuild()
    return {"removed_chunks": len(results), "affected_files": len(by_file), **info}


def list_docs() -> list[dict]:
    """列出所有文档。"""
    try:
        idx = _Index()
        idx.load()
        counts = Counter(m["source"] for m in idx.meta)
        return [{"name": Path(s).name, "path": s, "chunks": n} for s, n in sorted(counts.items())]
    except FileNotFoundError:
        return []


def rebuild() -> dict:
    """重建全部索引。"""
    docs = _load_docs()
    ip = STORAGE_DIR / "index.json"
    mp = STORAGE_DIR / "metadata.json"
    if not docs:
        ip.unlink(missing_ok=True)
        mp.unlink(missing_ok=True)
        return {"documents": 0, "chunks": 0}
    chunks = _chunk_docs(docs)
    texts = [c["text"] for c in chunks]
    vectors = _embed(texts)
    meta = [{"source": c["source"], "chunk_index": c["chunk_index"], "text": c["text"]} for c in chunks]
    _Index().build(vectors, meta)
    return {"documents": len(docs), "chunks": len(chunks)}


def clear() -> dict:
    """清空知识库。"""
    removed = 0
    for fp in KB_PATH.rglob("*"):
        if fp.suffix.lower() in SUFFIXES and fp.is_file():
            if "storage" in fp.parts or fp.name in CONFIG_FILES:
                continue
            fp.unlink()
            removed += 1
    (STORAGE_DIR / "index.json").unlink(missing_ok=True)
    (STORAGE_DIR / "metadata.json").unlink(missing_ok=True)
    return {"removed_files": removed}


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description="RAG 知识库")
    sp = p.add_subparsers(dest="cmd")

    a = sp.add_parser("add", help="添加笔记")
    a.add_argument("title", help="标题")
    a.add_argument("content", nargs="+", help="内容")

    q = sp.add_parser("query", help="语义检索")
    q.add_argument("question", nargs="+", help="问题")
    q.add_argument("-k", "--top-k", type=int, default=None, help="返回条数")

    d = sp.add_parser("delete", help="智能删除")
    d.add_argument("content", nargs="+", help="要删除的内容描述")

    sp.add_parser("list", help="列出文档")
    sp.add_parser("rebuild", help="重建索引")
    sp.add_parser("clear", help="清空知识库")

    args = p.parse_args()

    if args.cmd is None:
        p.print_help()
        sys.exit(0)

    if not EMBEDDING_API_KEY:
        print(f"错误: EMBEDDING_API_KEY 未在 {_ENV_FILE} 中设置")
        sys.exit(1)

    if args.cmd == "add":
        r = add(args.title, " ".join(args.content))
        print(f"已添加: {r['title']} ({r['chunks']} chunks)")

    elif args.cmd == "query":
        results = query(" ".join(args.question), args.top_k)
        if not results:
            print("(无结果)")
        for i, r in enumerate(results, 1):
            name = Path(r["source"]).name
            print(f"\n── [{i}] {name} chunk{r['chunk_index']} dist={r['distance']:.4f} ──")
            print(r["text"][:600])

    elif args.cmd == "delete":
        r = delete(" ".join(args.content))
        print(f"已删除: {r['removed_chunks']} chunks ({r['affected_files']} 文件)")
        print(f"  剩余: {r['documents']} 文档, {r['chunks']} chunks")

    elif args.cmd == "list":
        docs = list_docs()
        if not docs:
            print("(知识库为空)")
            return
        total = sum(d["chunks"] for d in docs)
        print(f"知识库: {len(docs)} 个文档, {total} 个 chunks\n")
        for d in docs:
            print(f"  {d['name']}  ({d['chunks']} chunks)")

    elif args.cmd == "rebuild":
        r = rebuild()
        print(f"索引完成: {r['documents']} 个文档, {r['chunks']} 个 chunks")

    elif args.cmd == "clear":
        r = clear()
        print(f"已清空: {r['removed_files']} 个文件")


if __name__ == "__main__":
    main()
