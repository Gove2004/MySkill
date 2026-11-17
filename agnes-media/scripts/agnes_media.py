#!/usr/bin/env python3
"""Agnes AI Media Tool — Generate images and videos using Base64 only"""

import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
import urllib.request
import urllib.error
import argparse

# ── Configuration loading (embedded, no external module dependency) ───────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_ENV_FILE = _SCRIPT_DIR.parent / ".env"


def _load_env():
    if not _ENV_FILE.exists():
        return {}
    env = {}
    with open(_ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip("'\"")
    return env


_env = _load_env()
API_KEY = _env.get("AGNES_API_KEY", "").strip()
BASE_URL = _env.get("AGNES_BASE_URL", "https://api.agnes-ai.cn/v1").rstrip("/")

if not API_KEY:
    print("[ERROR] AGNES_API_KEY not set. Please copy .env.example -> .env and fill in real key.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def _post_json(url, headers, body, timeout=60):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        content = e.fp.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"{e.code}: {content}") from e
    except Exception as e:
        raise RuntimeError(f"POST failed: {e}") from e


def _get_json(url, headers=None, timeout=60):
    h = headers or {"Authorization": f"Bearer {API_KEY}"}
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        content = e.fp.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"{e.code}: {content}") from e
    except Exception as e:
        raise RuntimeError(f"GET failed: {e}") from e


def _read_local_file_to_base64(file_path):
    """Read a local file and encode it as Base64 string."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Local file not found: {file_path}")
    if os.path.isdir(file_path):
        raise IsADirectoryError(f"Is a directory, not a file: {file_path}")
    with open(file_path, "rb") as f:
        content = f.read()
    import base64
    return base64.b64encode(content).decode("utf-8")


def _collect_image_inputs(local_files):
    """Collect image inputs from local file paths only — auto-encoded to Base64."""
    inputs = []
    if local_files:
        for lf in local_files:
            try:
                b64 = _read_local_file_to_base64(lf)
                inputs.append(f"data:image/png;base64,{b64}")
                print(f"[INFO] Read and encoded local file: {lf} ({len(b64)} chars)")
            except FileNotFoundError:
                print(f"[WARNING] File not found, skipping: {lf}")
            except IsADirectoryError:
                print(f"[WARNING] Skipped directory: {lf}")
            except Exception as e:
                print(f"[WARNING] Error reading file {lf}: {e}")
                continue
    return inputs


def request_image(prompt, image_inputs, size="2K", ratio="1:1", seed=None):
    url = f"{BASE_URL}/images/generations"
    payload = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "size": size,
        "ratio": ratio,
        "extra_body": {"image": image_inputs, "response_format": "b64_json"},
    }

    if seed is not None:
        payload["seed"] = seed

    print(f"[INFO] Generating image with model={payload['model']}, size={size}, ratio={ratio}")
    if image_inputs:
        print(f"[INFO] Using {len(image_inputs)} reference image(s)")
    if seed is not None:
        print(f"[INFO] Seed: {seed}")

    try:
        result = _post_json(url, headers, payload)
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        return None

    data = result.get("data", [])
    if not data:
        print("[ERROR] No 'data' field in response")
        return None

    item = data[0]
    b64 = item.get("b64_json", "")
    if not b64:
        print("[ERROR] No 'b64_json' field in response")
        # Fallback: check for any URL-like value
        for val in item.values():
            if isinstance(val, str) and val.startswith("http"):
                print(f"[WARNING] Found URL fallback: {val}")
                # Try downloading the URL and converting to Base64
                try:
                    req = urllib.request.Request(val)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        content = resp.read()
                    import base64
                    b64 = base64.b64encode(content).decode("utf-8")
                    print(f"[INFO] Converted URL image to Base64 ({len(b64)} chars)")
                except Exception as ex:
                    print(f"[ERROR] Failed to convert URL image: {ex}")
                    raise RuntimeError("No valid Base64 or URL found in response")

    print(f"[SUCCESS] Image generated, saved to temp file")
    tmp_path = _write_base64_to_temp(b64, "image")
    if tmp_path:
        print(f"[Image saved to: {tmp_path}]")
    return tmp_path


def _write_base64_to_temp(b64_data, media_type="image"):
    """Write Base64 data to a temporary file and return the path."""
    ext = "png" if media_type == "image" else "mp4"
    fd, path = tempfile.mkstemp(suffix=f".{ext}", prefix="agnes_")
    try:
        import base64
        decoded = base64.b64decode(b64_data)
        with os.fdopen(fd, "wb") as f:
            f.write(decoded)
        print(f"[INFO] Created temp file: {path} ({len(decoded)} bytes)")
        return path
    except Exception as e:
        print(f"[WARNING] Could not write temp file: {e}")
        try:
            os.close(fd)
            os.unlink(path)
        except:
            pass
        return None


def request_video(prompt, image_url=None, mode="text2video", width=1152, height=768,
                  num_frames=121, frame_rate=24, seed=None, negative_prompt=None,
                  max_wait=180, poll_interval=5, extra_images=None, inference_steps=None):
    model = "agnes-video-v2.0"
    vurl = f"{BASE_URL}/videos"

    payload = {
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }

    if extra_images:
        payload["extra_body"] = {"image": extra_images, "mode": "keyframes"}
    elif image_url:
        payload["image"] = image_url

    if seed is not None:
        payload["seed"] = seed
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if inference_steps is not None:
        payload["num_inference_steps"] = inference_steps

    print(f"[INFO] Creating video task: {model}, {num_frames} frames @ {frame_rate}fps")
    if image_url:
        print(f"[INFO] Image input provided (ti2vid)")
    elif extra_images:
        print(f"[INFO] Keyframe animation: {len(extra_images)} images")
    print(f"[INFO] Max wait: {max_wait}s")

    try:
        resp = _post_json(vurl, headers, payload)
    except Exception as e:
        print(f"[ERROR] Task creation failed: {e}")
        return None

    task_id = resp.get("task_id", "")
    video_id = resp.get("video_id", "")
    status = resp.get("status", "unknown")
    print(f"[SUCCESS] Task submitted: task_id={task_id}, status={status}")

    start = time.time()
    while time.time() - start < max_wait:
        try:
            status_resp = _get_json(f"{BASE_URL}/agnesapi?video_id={video_id}")
        except Exception as e:
            print(f"[ERROR] Polling failed: {e}")
            break

        st = status_resp.get("status", "")
        pr = status_resp.get("progress", 0)
        print(f"\rProgress {pr}/100, status: {st}", end="", flush=True)

        if st == "completed":
            break
        elif st == "failed":
            err = status_resp.get("error", {})
            print(f"\n[ERROR] Video generation failed: {err}")
            return None
        time.sleep(poll_interval)

    print()
    print("[INFO] Retrieving video result...")

    # First, check for direct 'url' field in the response
    if status_resp.get("url"):
        video_url = status_resp["url"]
        print(f"[SUCCESS] Video found directly: {video_url[:80]}...")
        tmp_path = _download_and_save_video(video_url, filename="output.mp4")
        if tmp_path:
            print(f"[Video saved to: {tmp_path}]")
        return tmp_path

    # Search for HTTP URL in the response
    def find_http_url(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://")):
                    if any(ext in v.lower() for ext in ['.mp4', '.mov', '.video']):
                        return v, f"{path}.{k}"
                result = find_http_url(v, f"{path}.{k}")
                if result:
                    return result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result = find_http_url(item, f"{path}[{i}]")
                if result:
                    return result
        return None

    http_result = find_http_url(status_resp)
    if http_result:
        video_url, url_path = http_result
        print(f"[SUCCESS] Video found at {url_path}]")
        tmp_path = _download_and_save_video(video_url, filename="output.mp4")
        if tmp_path:
            print(f"[Video saved to: {tmp_path}]")
        return tmp_path
    else:
        # Try fallback via task_id endpoint
        try:
            old_endpoint = f"{BASE_URL}/videos/{task_id}" if task_id else ""
            if old_endpoint:
                old_resp = _get_json(old_endpoint)
                if old_resp.get("url"):
                    video_url = old_resp["url"]
                    print(f"[SUCCESS] Video found directly in fallback: {video_url[:80]}...")
                    tmp_path = _download_and_save_video(video_url, filename="output.mp4")
                    if tmp_path:
                        print(f"[Video saved to: {tmp_path}]")
                    return tmp_path

                http_result_old = find_http_url(old_resp)
                if http_result_old:
                    video_url, url_path = http_result_old
                    print(f"[SUCCESS] Video found via fallback: {url_path}]")
                    tmp_path = _download_and_save_video(video_url, filename="output.mp4")
                    if tmp_path:
                        print(f"[Video saved to: {tmp_path}]")
                    return tmp_path
        except Exception as e:
            print(f"[WARNING] Fallback error: {e}")

        print("[WARNING] Video URL could not be retrieved from API. The video may have been generated but URL not found in response.")
        if status_resp:
            print(f"[DEBUG] Response keys: {list(status_resp.keys())}")
        return None


def _download_and_save_video(url, filename="output.mp4"):
    """Download video from URL and save to file."""
    print(f"[Saving] Downloading video from {url}...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        with open(filename, "wb") as f:
            f.write(content)
        print(f"   [Success]: {len(content)} bytes saved to {filename}")
        return filename
    except Exception as e:
        print(f"   [Error]: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "image":
        parse_image(sys.argv[2:])
    elif cmd == "video":
        parse_video(sys.argv[2:])
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        usage()
        sys.exit(1)


def usage():
    print("""Agnes AI Media Tool — Generate images and videos (Base64 only)

Usage:
  agnes-media [command] [args...]

Commands:
  image    Image generation (supports local file input)
  video    Video generation (text-to-video / image-to-video / keyframe animation)

Examples:
  agnes-media image "Cyberpunk cat, golden eyes" --size 2K --ratio 16:9 --input-file ./cat.jpg
  agnes-media video "Dog on waves" --width 768 --height 1365 --num-frames 81
""")


def parse_image(args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("prompt", help="Image prompt (required)")
    parser.add_argument("--input-file", dest="local_files", nargs="+", required=False,
                        help="Local image file(s) for reference (auto-encoded to Base64). If omitted, pure text-to-image")
    parser.add_argument("--size", default="2K", choices=["1K", "2K", "3K", "4K"],
                        help="Output size preset (default 2K)")
    parser.add_argument("--ratio", default="1:1",
                        help=f"Aspect ratio (default 1:1, options: 1:1 3:4 4:3 16:9 9:16 2:3 3:2 21:9)")
    parser.add_argument("--seed", type=int, metavar="N", help="Seed (for reproducibility)")

    opts, unknown = parser.parse_known_args(args)
    if unknown:
        print(f"[WARNING] Ignoring unknown arguments: {unknown}")

    combined = _collect_image_inputs(opts.local_files) if opts.local_files else []

    if not combined and not opts.prompt:
        print("[ERROR] Prompt is required")
        sys.exit(1)

    request_result = request_image(
        prompt=opts.prompt,
        image_inputs=combined,
        size=opts.size,
        ratio=opts.ratio,
        seed=opts.seed,
    )
    if request_result:
        print(f"[Image saved to: {request_result}]")


def parse_video(args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("prompt", help="Video prompt (required)")
    parser.add_argument("--image", dest="image_url",
                        help="Image-to-video (ti2vid): single image URL or local file path")
    parser.add_argument("--extra-image", dest="extra_images", nargs="+",
                        help="Keyframe animation: image URLs or local file paths (auto-encoded)")
    parser.add_argument("--mode", default="text2video", choices=["text2video", "keyframes"],
                        help="Generation mode (default text2video, use keyframes for animation)")
    parser.add_argument("--width", type=int, default=1152, help="Video width in pixels (default 1152)")
    parser.add_argument("--height", type=int, default=768, help="Video height in pixels (default 768)")
    parser.add_argument(
        "--num-frames", type=int, default=121,
        help="Number of frames (must be <=441 and satisfy 8n+1, default 121)"
    )
    parser.add_argument(
        "--fps", type=int, default=24,
        help="Frame rate (1-60, default 24)"
    )
    parser.add_argument("--seed", type=int, metavar="N", help="Seed (for reproducibility)")
    parser.add_argument("--negative-prompt", dest="negative_prompt",
                        help="Negative prompt (content to avoid)")
    parser.add_argument(
        "--inference-steps", dest="inference_steps", type=int,
        help="Inference steps (fewer = faster, optional)"
    )

    opts, unknown = parser.parse_known_args(args)
    if unknown:
        print(f"[WARNING] Ignoring unknown arguments: {unknown}")

    n = (opts.num_frames - 1) // 8
    if (8 * n + 1 != opts.num_frames) or opts.num_frames > 441 or opts.num_frames < 1:
        print("[ERROR] num_frames must be <=441 and satisfy 8n+1. Recommended: 81, 121, 241, 441")
        sys.exit(1)

    # Process local files for extra_images
    extra_imgs = []
    if opts.extra_images:
        for img in opts.extra_images:
            if os.path.exists(img) and os.path.isfile(img):
                try:
                    b64 = _read_local_file_to_base64(img)
                    extra_imgs.append(f"data:image/png;base64,{b64}")
                    print(f"[INFO] Encoded local file for keyframe: {img}")
                except Exception as e:
                    print(f"[WARNING] Could not encode {img}: {e}")
                    # Treat as URL if encoding fails
                    if not img.startswith("data:"):
                        extra_imgs.append(f"data:image/png;base64,{img}")
            elif img.startswith(("http://", "https://")) or img.startswith("data:"):
                extra_imgs.append(img)
            else:
                print(f"[WARNING] Unrecognized input: {img}, skipping")

    # Process image_url — could be URL or local file
    image_url_processed = None
    if opts.image_url:
        if os.path.exists(opts.image_url) and os.path.isfile(opts.image_url):
            try:
                b64 = _read_local_file_to_base64(opts.image_url)
                image_url_processed = f"data:image/png;base64,{b64}"
                print(f"[INFO] Encoded local file for image-to-video: {opts.image_url}")
            except Exception as e:
                print(f"[ERROR] Could not encode local file for ti2vid: {e}")
                sys.exit(1)
        elif opts.image_url.startswith(("http://", "https://")):
            image_url_processed = opts.image_url
        else:
            print(f"[WARNING] Unrecognized image URL/file: {opts.image_url}, skipping")

    request_result = request_video(
        prompt=opts.prompt,
        image_url=image_url_processed,
        mode=opts.mode,
        width=opts.width,
        height=opts.height,
        num_frames=opts.num_frames,
        frame_rate=opts.fps,
        seed=opts.seed,
        negative_prompt=opts.negative_prompt,
        inference_steps=opts.inference_steps,
        extra_images=extra_imgs if extra_imgs else None,
    )
    if request_result:
        print(f"[Video saved to: {request_result}]")


if __name__ == "__main__":
    main()