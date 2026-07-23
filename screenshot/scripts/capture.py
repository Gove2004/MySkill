"""Screenshot capture tool — Windows only, requires Pillow.

Usage:
  python capture.py full <output.png>
  python capture.py region <x> <y> <w> <h> <output.png>
  python capture.py window <title-substring> <output.png>
  python capture.py scout [scale] <output.png>
  python capture.py list
"""

import sys
import ctypes
from ctypes import wintypes

# Force UTF-8 stdout so window titles with non-GBK characters don't crash
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# DPI awareness — use system DPI so coordinates match physical pixels
ctypes.windll.shcore.SetProcessDpiAwareness(1)

from PIL import ImageGrab


def capture_full(output):
    """Capture entire virtual screen (all monitors)."""
    img = ImageGrab.grab(all_screens=True)
    img.save(output)
    print(f"Full screenshot: {output} ({img.width}x{img.height})")


def capture_region(x, y, w, h, output):
    """Capture a specific bounding-box region."""
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(output)
    print(f"Region screenshot: {output} ({w}x{h} @ {x},{y})")


def capture_window(substr, output):
    """Find the first visible window whose title contains `substr` (case-insensitive)
    and capture its client area."""
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    result = []

    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        if substr.lower() in title.lower():
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if rect.left > -1000 and rect.top > -1000:
                result.append((title, rect.left, rect.top, rect.right, rect.bottom, hwnd))
                return False
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)

    if not result:
        print(f"No visible window found matching: {substr}")
        sys.exit(1)

    title, left, top, right, bottom, _hwnd = result[0]
    w, h = right - left, bottom - top
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    img.save(output)
    print(f"Window screenshot: {output} ({w}x{h}) — \"{title}\"")


def capture_scout(output, scale=4):
    """Capture full screen downscaled by `scale` for AI preview."""
    img = ImageGrab.grab(all_screens=True)
    sw, sh = img.width // scale, img.height // scale
    img = img.resize((sw, sh), ImageGrab.Image.LANCZOS)
    img.save(output)
    print(f"Scout screenshot: {output} ({sw}x{sh}, 1/{scale})")


def list_windows():
    """Print all visible windows with titles and positions."""
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        if not title:
            return True
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        # Skip hidden/minimized windows (negative coords)
        if rect.left < -1000 or rect.top < -1000:
            return True
        w, h = rect.right - rect.left, rect.bottom - rect.top
        if w > 0 and h > 0:
            print(f"[{rect.left},{rect.top} {w}x{h}] {title}")
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "full":
        if len(sys.argv) != 3:
            print("Usage: python capture.py full <output.png>")
            sys.exit(1)
        capture_full(sys.argv[2])

    elif mode == "region":
        if len(sys.argv) != 7:
            print("Usage: python capture.py region <x> <y> <w> <h> <output.png>")
            sys.exit(1)
        x, y, w, h = map(int, sys.argv[2:6])
        capture_region(x, y, w, h, sys.argv[6])

    elif mode == "window":
        if len(sys.argv) != 4:
            print("Usage: python capture.py window <title-substring> <output.png>")
            sys.exit(1)
        capture_window(sys.argv[2], sys.argv[3])

    elif mode == "scout":
        if len(sys.argv) == 3:
            capture_scout(sys.argv[2])
        elif len(sys.argv) == 4:
            capture_scout(sys.argv[3], scale=int(sys.argv[2]))
        else:
            print("Usage: python capture.py scout [scale] <output.png>")
            sys.exit(1)

    elif mode == "list":
        list_windows()

    else:
        print(f"Unknown mode: {mode}")
        print(__doc__)
        sys.exit(1)