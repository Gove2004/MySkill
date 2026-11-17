---
name: pdf-to-markdown
description: Convert PDF (and Word/PPT/Excel/image/HTML) files to clean Markdown via the MinerU API. Use whenever you need to read a PDF, extract text, parse a document, analyze document contents, or the user asks 读PDF, 解析文档, 把PDF转成Markdown, 提取文档内容, 看看这个PDF. Better than raw PDF reading — handles tables, formulas, multi-column layouts, scanned docs. Bundles a ready-to-run script using the configured MinerU token — invoke it instead of reading PDFs directly with the Read tool or writing ad-hoc parsers.
---

# PDF to Markdown

Convert documents (PDF, Word, PPT, Excel, images, HTML) to clean, structured Markdown via the MinerU API. Produces far better results than raw PDF reading tools — handles tables, formulas, multi-column layouts, and scanned documents.

## Quick start

```bash
python scripts/parse_pdf.py --pdf <path>
```

This defaults to Precision API (vlm model) with the token configured in `.env`. The script uploads the file, polls until done, saves `<name>.md` alongside the PDF, and prints a preview.

After the script completes, read the `.md` file with the Read tool to present content to the user.

## API choice

| Condition | Mode |
|---|---|
| File ≤ 200MB, ≤ 200 pages, token available | `--mode precision` (default) |
| File ≤ 10MB, ≤ 20 pages, quick check or token unavailable | `--mode agent` |

If the Agent API rejects a file (too large / too many pages), the script tells you to switch to `--mode precision`. If the Precision API token is expired, fall back to `--mode agent`.

## Common options

| Flag | Description |
|---|---|
| `--pdf <path>` | File path (required). Supports .pdf, .doc, .docx, .ppt, .pptx, .xls, .xlsx, images, .html |
| `--mode precision\|agent` | API tier (default: precision) |
| `--url <url>` | Submit a remote file URL directly instead of uploading a local file |
| `--output <dir>` | Output directory (default: same as input file) |
| `--language <code>` | Document language (default: ch). See `references/languages.md` for full list |
| `--page-ranges <range>` | Parse specific pages, e.g. `"1-10"` or `"2,4-6"` (precision) / `"1-10"` (agent) |
| `--ocr` | Enable OCR for scanned documents (precision/agent, PDF only) |
| `--no-table` | Disable table recognition (faster, lower quality) |
| `--no-formula` | Disable formula recognition (faster, lower quality) |
| `--model <name>` | Model version for precision mode: `vlm` (default, best), `pipeline`, `MinerU-HTML` (for HTML files) |
| `--extra-formats <fmt>` | Additional output formats beyond Markdown: `docx`, `html`, `latex` (precision only, comma-separated) |
| `--timeout <seconds>` | Max wait time (default: 600 precision, 300 agent) |

## Precision API (recommended)

- **Model**: `vlm` (best quality for complex layouts, formulas, tables)
- **Output**: ZIP containing Markdown + JSON + optional DOCX/HTML/LaTeX
- **Token**: stored in `.env` file at skill root (`MINERU_TOKEN=...`)
- **Limits**: 200MB, 200 pages, 1000 priority pages/day

If the token is missing or expired, the script falls back to Agent mode automatically.

### Two submission paths

1. **Local file upload** (default): Script requests a signed upload URL, PUTs the file, then polls. Use `--pdf <path>`.
2. **Remote URL** (faster, no upload): File already on a server? Use `--url <url>` to submit directly. The API downloads it server-side.

## Agent lightweight API (fallback)

- **No token required** (IP rate-limited, 429 if exceeded)
- **Output**: Markdown CDN link only
- **Limits**: 10MB, 20 pages
- Use for quick checks or when the token is unavailable

Also supports `--url` mode: `--mode agent --url <url>` submits a remote file URL without uploading.

## Error recovery

| Script message | Action |
|---|---|
| "Token 错误" / "Token 过期" | Switch to `--mode agent` |
| "文件大小超出限制" (agent) | Switch to `--mode precision` |
| "文件页数超过限制" (agent) | Switch to `--mode precision` or use `--page-ranges` |
| "429" (agent) | Wait a minute and retry |
| "每日解析任务数量已达上限" (precision) | Switch to `--mode agent` or wait until tomorrow |

## Supported file types

| Format | Precision | Agent |
|---|---|---|
| PDF | Yes | Yes |
| PNG/JPG/JPEG/JP2/WebP/GIF/BMP | Yes | Yes |
| DOC/DOCX | Yes | Yes |
| PPT/PPTX | Yes | Yes |
| XLS/XLSX | Yes | Yes |
| HTML | Yes (use `--model MinerU-HTML`) | No |

## Language codes

Common values: `ch` (default, Chinese+English), `en` (English only), `japan`, `korean`, `chinese_cht` (traditional), `latin`, `arabic`, `cyrillic`, `devanagari`.

See `references/languages.md` for the complete table.
