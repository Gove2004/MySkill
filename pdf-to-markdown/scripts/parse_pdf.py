#!/usr/bin/env python3
"""Parse documents to Markdown using MinerU API (stdlib only, no pip deps).

Supports: PDF, Word, PPT, Excel, images, HTML.
Two API tiers: Precision (token required) and Agent (no token, lightweight).

Usage:
    python parse_pdf.py --pdf <path>
    python parse_pdf.py --pdf <path> --mode agent
    python parse_pdf.py --url <url> --mode precision
    python parse_pdf.py --pdf <path> --language en --ocr --extra-formats docx
"""

import argparse
import io
import json
import os
import sys
import time
import zipfile
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


def _load_token():
    """Load MinerU token from .env file (relative to this script)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "..", ".env"),   # skill root
        os.path.join(script_dir, ".env"),          # scripts/
    ]
    for env_path in candidates:
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() == "MINERU_TOKEN":
                        return v.strip().strip('"').strip("'")
        except FileNotFoundError:
            continue
    return None


TOKEN = _load_token()

PRECISION_ERRORS = {
    "A0202": "Token error — check the token is correct",
    "A0211": "Token expired — please renew your token",
    -500: "Parameter error — check content-type and parameter types",
    -10001: "Service error — please retry later",
    -10002: "Request parameter error — check request format",
    -60001: "Failed to generate upload URL — retry later",
    -60002: "Failed to detect file format — check file extension",
    -60003: "Failed to read file — check if file is corrupted",
    -60004: "Empty file — upload a valid file",
    -60005: "File size exceeds limit (max 200MB)",
    -60006: "Page count exceeds limit (max 200 pages)",
    -60007: "Model service temporarily unavailable — retry later",
    -60008: "File read timeout — check URL accessibility",
    -60009: "Task queue full — retry later",
    -60010: "Parse failed — retry later",
    -60011: "Failed to get valid file — ensure file is uploaded",
    -60012: "Task not found — check task_id is valid and not deleted",
    -60013: "No permission to access this task",
    -60014: "Cannot delete running task",
    -60015: "File conversion failed — try converting to PDF manually",
    -60016: "File conversion failed — try other formats or retry",
    -60017: "Retry limit reached — wait for model upgrade",
    -60018: "Daily parse quota exceeded — try tomorrow",
    -60019: "HTML file parse quota exceeded — try tomorrow",
    -60020: "File split failed — retry later",
    -60021: "Failed to read page count — retry later",
    -60022: "Webpage read failed — network issue or rate limiting",
}

AGENT_ERRORS = {
    -30001: "File size exceeds agent limit (10MB) — use --mode precision",
    -30002: "Agent API does not support this file type",
    -30003: "Page count exceeds agent limit — use --mode precision or --page-ranges",
    -30004: "Request parameter error — check required parameters",
}


# ── HTTP helpers ────────────────────────────────────────────────────────

def _api_post(url, body=None, headers=None):
    """POST JSON to url, return parsed JSON response."""
    data = json.dumps(body).encode("utf-8") if body else None
    hdrs = headers or {}
    if body is not None and "Content-Type" not in hdrs:
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        try:
            return json.loads(body_bytes)
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {body_bytes.decode('utf-8', errors='replace')[:300]}")


def _api_get(url, headers=None):
    """GET url, return parsed JSON response."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        try:
            return json.loads(body_bytes)
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {body_bytes.decode('utf-8', errors='replace')[:300]}")


def _api_put(url, data_bytes):
    """PUT raw bytes to a signed OSS URL.

    Uses low-level http.client because the OSS pre-signed URL is extremely
    header-sensitive — urllib may auto-add Content-Type or Transfer-Encoding
    headers that invalidate the signature.
    """
    from urllib.parse import urlparse
    import http.client

    parsed = urlparse(url)
    if parsed.scheme == "https":
        conn = http.client.HTTPSConnection(parsed.hostname)
    else:
        conn = http.client.HTTPConnection(parsed.hostname)

    path = parsed.path + ("?" + parsed.query if parsed.query else "")
    conn.request("PUT", path, body=data_bytes)
    resp = conn.getresponse()
    status = resp.status
    resp.read()  # drain body
    conn.close()
    return status


def _api_download(url):
    """Download raw bytes from url."""
    with urllib.request.urlopen(url) as resp:
        return resp.read()


# ── Shared utilities ────────────────────────────────────────────────────

def _get_filename(source_path=None, source_url=None):
    if source_path:
        return os.path.basename(source_path)
    if source_url:
        return source_url.rstrip("/").split("/")[-1] or "document.pdf"
    return "document.pdf"


def _safe_api_name(filename):
    """ASCII-safe filename for API submission (non-ASCII may be rejected)."""
    try:
        filename.encode("ascii")
        return filename
    except UnicodeEncodeError:
        _, ext = os.path.splitext(filename)
        return f"document{ext}" if ext else "document.pdf"


def _output_path(filename, output_dir):
    base = os.path.splitext(filename)[0]
    return os.path.join(output_dir, f"{base}.md")


def _save_markdown(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _preview(path):
    print("\n" + "=" * 60)
    print("Preview (first 500 chars):")
    print("=" * 60)
    with open(path, encoding="utf-8") as f:
        print(f.read()[:500])
    print("=" * 60)
    print(f"\nFull content saved to: {path}")


def _check_precision(result, label="request"):
    code = result.get("code")
    if code is not None and code != 0:
        msg = result.get("msg", "unknown")
        hint = PRECISION_ERRORS.get(code, "")
        raise RuntimeError(f"Precision API {label} failed (code={code}): {msg}. {hint}")


def _check_agent(result, label="request"):
    code = result.get("code")
    if code is not None and code != 0:
        msg = result.get("msg", "unknown")
        raise RuntimeError(f"Agent API {label} failed (code={code}): {msg}")


# ── Precision API ───────────────────────────────────────────────────────

def parse_precision_file(pdf_path, output_dir, language="ch", page_ranges=None,
                         ocr=False, enable_table=True, enable_formula=True,
                         model="vlm", extra_formats=None, timeout=600):
    """Precision API via batch file upload."""
    filename = _get_filename(source_path=pdf_path)
    api_name = _safe_api_name(filename)

    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    file_entry = {"name": api_name}
    if page_ranges:
        file_entry["page_ranges"] = page_ranges
    if ocr:
        file_entry["is_ocr"] = True

    body = {
        "files": [file_entry],
        "model_version": model,
        "enable_table": enable_table,
        "enable_formula": enable_formula,
        "language": language,
    }
    if extra_formats:
        body["extra_formats"] = extra_formats

    print(f"[precision] Getting upload URL for {filename}...")
    result = _api_post("https://mineru.net/api/v4/file-urls/batch", body, auth_headers)
    _check_precision(result, "get upload URL")

    batch_id = result["data"]["batch_id"]
    file_url = result["data"]["file_urls"][0]
    print(f"[precision] batch_id: {batch_id}")

    print("[precision] Uploading file...")
    with open(pdf_path, "rb") as f:
        status = _api_put(file_url, f.read())
    if status not in (200, 201):
        raise RuntimeError(f"Upload failed: HTTP {status}")
    print("[precision] Upload done, waiting for parse...")

    zip_url = _poll_precision_batch(batch_id, auth_headers, timeout)
    return _extract_precision_zip(zip_url, filename, output_dir)


def parse_precision_url(url, output_dir, filename=None, language="ch",
                        page_ranges=None, ocr=False, enable_table=True,
                        enable_formula=True, model="vlm", extra_formats=None,
                        timeout=600):
    """Precision API via single-file URL submission (no upload needed)."""
    filename = filename or _get_filename(source_url=url)

    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    body = {
        "url": url,
        "model_version": model,
        "enable_table": enable_table,
        "enable_formula": enable_formula,
        "language": language,
    }
    if page_ranges:
        body["page_ranges"] = page_ranges
    if ocr:
        body["is_ocr"] = True
    if extra_formats:
        body["extra_formats"] = extra_formats

    print(f"[precision] Submitting URL: {url}")
    result = _api_post("https://mineru.net/api/v4/extract/task", body, auth_headers)
    _check_precision(result, "submit URL")

    task_id = result["data"]["task_id"]
    print(f"[precision] task_id: {task_id}")

    zip_url = _poll_precision_task(task_id, auth_headers, timeout)
    return _extract_precision_zip(zip_url, filename, output_dir)


def _poll_precision_task(task_id, headers, timeout):
    """Poll Precision single-file task until done, return zip URL."""
    start = time.time()
    while time.time() - start < timeout:
        result = _api_get(
            f"https://mineru.net/api/v4/extract/task/{task_id}", headers
        )
        _check_precision(result, "poll task")

        data = result["data"]
        state = data["state"]
        elapsed = int(time.time() - start)

        if state == "done":
            full_zip_url = data["full_zip_url"]
            print(f"[{elapsed}s] Parse done, downloading result...")
            return full_zip_url
        if state == "failed":
            msg = data.get("err_msg", "unknown")
            raise RuntimeError(f"[{elapsed}s] Parse failed: {msg}")

        progress = data.get("extract_progress", {})
        pages_info = ""
        if progress:
            pages_info = f" ({progress.get('extracted_pages', '?')}/{progress.get('total_pages', '?')} pages)"
        print(f"[{elapsed}s] State: {state}{pages_info}...")
        time.sleep(5)

    raise RuntimeError(f"Timeout ({timeout}s) waiting for parse. task_id: {task_id}")


def _poll_precision_batch(batch_id, headers, timeout):
    """Poll Precision batch until done, return zip URL."""
    start = time.time()
    while time.time() - start < timeout:
        result = _api_get(
            f"https://mineru.net/api/v4/extract-results/batch/{batch_id}", headers
        )
        _check_precision(result, "poll batch")

        extract = result["data"]["extract_result"][0]
        state = extract["state"]
        elapsed = int(time.time() - start)

        if state == "done":
            full_zip_url = extract["full_zip_url"]
            print(f"[{elapsed}s] Parse done, downloading result...")
            return full_zip_url
        if state == "failed":
            msg = extract.get("err_msg", "unknown")
            raise RuntimeError(f"[{elapsed}s] Parse failed: {msg}")

        progress = extract.get("extract_progress", {})
        pages_info = ""
        if progress:
            pages_info = f" ({progress.get('extracted_pages', '?')}/{progress.get('total_pages', '?')} pages)"
        print(f"[{elapsed}s] State: {state}{pages_info}...")
        time.sleep(5)

    raise RuntimeError(f"Timeout ({timeout}s) waiting for parse result.")


def _extract_precision_zip(zip_url, filename, output_dir):
    """Download zip, extract full.md, save to output."""
    zip_bytes = _api_download(zip_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        md_files = [n for n in zf.namelist() if n.endswith("full.md")]
        if not md_files:
            raise RuntimeError(f"No full.md in zip. Contents: {zf.namelist()}")
        md_content = zf.read(md_files[0]).decode("utf-8")

    out = _output_path(filename, output_dir)
    _save_markdown(md_content, out)
    print(f"[precision] Saved to: {out}")
    return out


# ── Agent API ───────────────────────────────────────────────────────────

def parse_agent_file(pdf_path, output_dir, language="ch", page_range=None,
                     ocr=False, enable_table=True, enable_formula=True,
                     timeout=300):
    """Agent API via signed file upload."""
    filename = _get_filename(source_path=pdf_path)
    file_size = os.path.getsize(pdf_path)
    if file_size > 10 * 1024 * 1024:
        raise RuntimeError(
            f"File is {file_size / 1024 / 1024:.1f}MB, exceeds Agent API 10MB limit. "
            "Use --mode precision instead."
        )

    print(f"[agent] Getting upload URL for {filename}...")
    data = {
        "file_name": filename,
        "language": language,
        "enable_table": enable_table,
        "enable_formula": enable_formula,
    }
    if page_range:
        data["page_range"] = page_range
    if ocr:
        data["is_ocr"] = True

    result = _api_post("https://mineru.net/api/v1/agent/parse/file", data)
    _check_agent(result, "get upload URL")

    task_id = result["data"]["task_id"]
    file_url = result["data"]["file_url"]
    print(f"[agent] task_id: {task_id}")

    print("[agent] Uploading...")
    with open(pdf_path, "rb") as f:
        status = _api_put(file_url, f.read())
    if status not in (200, 201):
        raise RuntimeError(f"Upload failed: HTTP {status}")
    print("[agent] Upload done, waiting for parse...")

    md_content = _poll_agent(task_id, timeout)
    out = _output_path(filename, output_dir)
    _save_markdown(md_content, out)
    print(f"[agent] Saved to: {out}")
    return out


def parse_agent_url(url, output_dir, filename=None, language="ch",
                    page_range=None, ocr=False, enable_table=True,
                    enable_formula=True, timeout=300):
    """Agent API via remote URL submission."""
    filename = filename or _get_filename(source_url=url)

    print(f"[agent] Submitting URL: {url}")
    data = {
        "url": url,
        "language": language,
        "enable_table": enable_table,
        "enable_formula": enable_formula,
    }
    if page_range:
        data["page_range"] = page_range
    if ocr:
        data["is_ocr"] = True

    result = _api_post("https://mineru.net/api/v1/agent/parse/url", data)
    _check_agent(result, "submit URL")

    task_id = result["data"]["task_id"]
    print(f"[agent] task_id: {task_id}")

    md_content = _poll_agent(task_id, timeout)
    out = _output_path(filename, output_dir)
    _save_markdown(md_content, out)
    print(f"[agent] Saved to: {out}")
    return out


def _poll_agent(task_id, timeout):
    """Poll Agent API until done, return markdown text."""
    start = time.time()
    while time.time() - start < timeout:
        result = _api_get(f"https://mineru.net/api/v1/agent/parse/{task_id}")
        state = result["data"]["state"]
        elapsed = int(time.time() - start)

        if state == "done":
            markdown_url = result["data"]["markdown_url"]
            print(f"[{elapsed}s] Parse done, downloading markdown...")
            md_bytes = _api_download(markdown_url)
            return md_bytes.decode("utf-8")

        if state == "failed":
            err_code = result["data"].get("err_code")
            err_msg = result["data"].get("err_msg", "unknown")
            hint = AGENT_ERRORS.get(err_code, "")
            raise RuntimeError(f"[{elapsed}s] Parse failed: {err_msg}. {hint}")

        print(f"[{elapsed}s] State: {state}...")
        time.sleep(3)

    raise RuntimeError(f"Timeout ({timeout}s) waiting for parse. task_id: {task_id}")


# ── CLI ─────────────────────────────────────────────────────────────────

def _run_agent(args, output_dir, enable_table, enable_formula, timeout):
    """Execute agent mode with the given args."""
    if args.url:
        return parse_agent_url(
            args.url, output_dir, filename=args.name,
            language=args.language, page_range=args.page_ranges,
            ocr=args.ocr, enable_table=enable_table,
            enable_formula=enable_formula, timeout=timeout,
        )
    else:
        return parse_agent_file(
            args.file_path, output_dir,
            language=args.language, page_range=args.page_ranges,
            ocr=args.ocr, enable_table=enable_table,
            enable_formula=enable_formula, timeout=timeout,
        )


def main():
    p = argparse.ArgumentParser(description="Parse documents to Markdown via MinerU API")

    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--pdf", "--file", dest="file_path",
                     help="Local file path (.pdf, .doc, .docx, .ppt, .pptx, .xls, .xlsx, images, .html)")
    src.add_argument("--url", dest="url",
                     help="Remote file URL (API downloads it server-side)")

    p.add_argument("--mode", choices=["precision", "agent"], default="precision",
                   help="API tier: precision (token, 200MB/200p) or agent (no token, 10MB/20p)")
    p.add_argument("--output", "-o", default=None,
                   help="Output directory (default: same as input file, or cwd for URL mode)")
    p.add_argument("--language", default="ch",
                   help="Document language (default: ch). See references/languages.md")
    p.add_argument("--page-ranges", default=None,
                   help="Page ranges, e.g. '1-10' or '2,4-6' (precision) / '1-10' (agent)")
    p.add_argument("--ocr", action="store_true",
                   help="Enable OCR for scanned documents")
    p.add_argument("--no-table", action="store_true",
                   help="Disable table recognition (faster)")
    p.add_argument("--no-formula", action="store_true",
                   help="Disable formula recognition (faster)")
    p.add_argument("--model", default="vlm", choices=["vlm", "pipeline", "MinerU-HTML"],
                   help="Model version for precision mode (default: vlm)")
    p.add_argument("--extra-formats", default=None,
                   help="Extra output formats, comma-separated: docx,html,latex (precision only)")
    p.add_argument("--timeout", type=int, default=None,
                   help="Max wait seconds (default: 600 precision, 300 agent)")
    p.add_argument("--name", default=None,
                   help="Output filename (without .md). Default: derived from input filename.")

    args = p.parse_args()

    if args.file_path and not os.path.exists(args.file_path):
        print(f"Error: file not found: {args.file_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output
    if not output_dir:
        if args.file_path:
            output_dir = os.path.dirname(args.file_path) or "."
        else:
            output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    enable_table = not args.no_table
    enable_formula = not args.no_formula
    extra_formats = args.extra_formats.split(",") if args.extra_formats else None
    timeout = args.timeout or (600 if args.mode == "precision" else 300)

    try:
        if args.mode == "precision":
            if TOKEN is None:
                print("[precision] No token found in .env, falling back to agent mode.")
                output_path = _run_agent(args, output_dir, enable_table, enable_formula, timeout)
            elif args.url:
                output_path = parse_precision_url(
                    args.url, output_dir, filename=args.name,
                    language=args.language, page_ranges=args.page_ranges,
                    ocr=args.ocr, enable_table=enable_table,
                    enable_formula=enable_formula, model=args.model,
                    extra_formats=extra_formats, timeout=timeout,
                )
            else:
                output_path = parse_precision_file(
                    args.file_path, output_dir,
                    language=args.language, page_ranges=args.page_ranges,
                    ocr=args.ocr, enable_table=enable_table,
                    enable_formula=enable_formula, model=args.model,
                    extra_formats=extra_formats, timeout=timeout,
                )
        else:
            output_path = _run_agent(args, output_dir, enable_table, enable_formula, timeout)

        _preview(output_path)

    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()