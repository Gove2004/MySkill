---
name: agnes-media
description: Generate images and videos via Agnes AI API — text-to-image, text-to-video, image-to-video, and keyframe animation. Use when the user asks to generate/create an image or video, draw something, 生成图片, 生成视频, 文生图, 图生视频, 画一张图, 做视频, or mentions Agnes AI. All I/O uses Base64 internally; pure Python stdlib, zero dependencies.
---

# Agnes AI Media Script — Base64 Only

Generate high-quality images and videos via Agnes AI API. **Text-to-image** (with local file reference), **text-to-video**, **image-to-video**, and **keyframe animation** all supported. All I/O uses Base64 internally. Zero external dependencies — pure Python stdlib.

## Setup

Copy `.env.example` to `.env`, fill in your API Key:

```bash
cp .env.example .env
# Edit AGNES_API_KEY
```

| Variable | Description | Default |
|----------|-------------|---------|
| `AGNES_API_KEY` | Agnes AI API Key (required) | — |
| `AGNES_BASE_URL` | API base URL | `https://api.agnes-ai.cn/v1` |

## Usage

All paths relative to skill root directory:

```bash
# Text-to-image with local file reference
python scripts/agnes_media.py image "prompt" --input-file ./local.jpg [options]

# Text-to-video
python scripts/agnes_media.py video "prompt" [options]

# Image-to-video (ti2vid) with local file
python scripts/agnes_media.py video "prompt" --image ./local.jpg [options]

# Keyframe animation with local files
python scripts/agnes_media.py video "prompt" --mode keyframes --extra-image ./img1.jpg --extra-image ./img2.jpg [options]
```

## Parameters

### Image command options

| Flag | Meaning | Default | Options |
|------|---------|---------|---------|
| `--input-file` | Local image file(s) to encode | required (multiple allowed) | local file paths |
| `--size` | Size preset | 2K | 1K / 2K / 3K / 4K |
| `--ratio` | Aspect ratio | 1:1 | 1:1, 3:4, 4:3, 16:9, 9:16, 2:3, 3:2, 21:9 |
| `--seed` | Seed (for reproducibility) | none | any integer |
| `--timeout` | Request timeout (seconds) | 60 | positive integer |

### Video command options

| Flag | Meaning | Default | Options |
|------|---------|---------|---------|
| `--image` | Image input for ti2vid (local or URL) | none | HTTP/HTTPS URL or local file path |
| `--extra-image` | Keyframe images (local or URL) | none | multiple inputs |
| `--mode` | Generation mode | text2video | text2video / keyframes |
| `--width` | Pixel width | 1152 | positive integer |
| `--height` | Pixel height | 768 | positive integer |
| `--num-frames` | Number of frames | 121 | ≤441, must satisfy 8n+1 |
| `--fps` | Frame rate | 24 | 1-60 (any integer) |
| `--seed` | Seed | none | any integer |
| `--negative-prompt` | Negative prompt | none | text |
| `--inference-steps` | Inference steps | none | positive integer (fewer = faster) |
| `--timeout` | Max wait time (seconds) | 180 | positive integer |

### Mode-specific parameters

| mode | Description | Required args |
|------|-------------|---------------|
| `text2video` (default) text-to-video | Generate video from text only | prompt |
| `ti2vid` image-to-video | Static image → animated video | `--image` |
| `keyframes` keyframe animation | Interpolation between multiple keyframes | `--mode keyframes` + `--extra-image` |

## Examples

**Text-to-image (reference local file, 2K, 16:9):**

```bash
python scripts/agnes_media.py image "Cyberpunk cat, golden eyes, neon lights" \
  --size 2K --ratio 16:9 --input-file ./cat.png
```

**Text-to-video (vertical short-form 9:16):**

```bash
python scripts/agnes_media.py video "Dog on waves, warm sunlight, slow motion" \
  --width 768 --height 1365 --num-frames 81 --fps 24
```

**Image-to-video (animate static cat from local file):**

```bash
python scripts/agnes_media.py video "Slow head turn, ear twitching" \
  --image ./cat.jpg --width 768 --height 1365
```

**Keyframe animation (day-to-night transition with local files):**

```bash
python scripts/agnes_media.py video "Room day-to-night transition" \
  --mode keyframes \
  --extra-image ./day.jpg \
  --extra-image ./night.jpg
```

## Technical Details

- **Image API**: `POST /images/generations`, model `agnes-image-2.1-flash`, synchronous
- **Video API**: `POST /videos` task creation, `GET /agnesapi?video_id=...` polling, model `agnes-video-v2.0`, asynchronous
- **Dependencies**: Python stdlib only (`json`, `argparse`, `urllib`, `pathlib`, `subprocess`, `os`, `time`, `tempfile`, `base64`)
- **Output**: Base64 data copied to clipboard and saved to temporary `.png`/`.mp4` file

## Notes

⏰ **Video generation is asynchronous** — script polls for completion. Default max wait: 180s (`--timeout` configurable).  
⚠️ `num_frames` must satisfy `8n+1` and ≤441. Recommended: 81(≈3s), 121(≈5s), 241(≈10s), 441(≈18s).  
⚠️ For image-to-video (`ti2vid`) and keyframes, provide local file paths with `--image` or `--extra-image`; they are automatically encoded to Base64.  
💡 **Tip**: Use `--input-file` for local images — no manual Base64 encoding needed!

## References

- [Agnes Image 2.1 Flash](https://www.agnes-ai.cn/zh-Hans/docs/agnes-image-21-flash)
- [Agnes Video V2.0](https://www.agnes-ai.cn/zh-Hans/docs/agnes-video-v20)