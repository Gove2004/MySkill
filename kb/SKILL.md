---
name: kb
description: RAG knowledge base. Use when user asks to record notes, query knowledge, search saved info, or delete content. Triggers on "记录", "记一下", "查一下", "知识库", "帮我查", "记录下来", "删除笔记", "搜一下".
---

# RAG 知识库

零外部依赖的本地 RAG 知识库。数据存储在 `DEFAULT_KB_PATH`（见 `.env`），CLI 脚本 `cli.py` 位于本 Skill 根目录。

核心原则：知识库只返回检索到的原文片段，你负责根据片段回答用户。

## 配置

复制 `.env.example` 为 `.env`，填入真实值：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `EMBEDDING_API_KEY` | SiliconFlow API key | — |
| `EMBEDDING_BASE_URL` | Embedding API 地址 | `https://api.siliconflow.cn/v1` |
| `EMBEDDING_MODEL` | Embedding 模型 | `Qwen/Qwen3-Embedding-4B` |
| `DEFAULT_KB_PATH` | 知识库数据目录 | `D:/Data/Knowledge` |
| `CHUNK_SIZE` | 分块大小 | `800` |
| `CHUNK_OVERLAP` | 分块重叠 | `100` |
| `TOP_K` | 默认检索条数 | `5` |

## 命令

所有路径相对于本 Skill 根目录：

```bash
python cli.py add "<标题>" "<内容>"
python cli.py query "<问题>" [-k N]
python cli.py delete "<内容描述>"
python cli.py list
python cli.py rebuild
python cli.py clear
```

## 命令说明

- **add** — 创建 .md → 分块 → embedding → 增量索引
- **query** — 语义检索，返回 `{source, chunk_index, text, distance}`，默认 top-5
- **delete** — 先 query 定位相关 chunks → 从源文件精准移除 → 重建索引
- **list** — 列出文档及 chunk 数
- **rebuild** — 从所有 .md/.txt 重建索引
- **clear** — 删除全部文档和索引

## 技术

零外部依赖（纯标准库）。Embedding：SiliconFlow Qwen3-Embedding-4B。向量搜索：纯 Python L2。