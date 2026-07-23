---
name: screenshot
description: Take screenshots and capture screen content. Use when the user asks to screenshot, 截图, 截屏, screen capture, take a picture of the screen, capture the screen, 截取屏幕, 截个图, or needs to see what's on screen. Supports AI-driven region selection via scout preview mode.
---

# Screenshot

Windows 截图工具，通过 Python + Pillow 提供五种捕获模式。

## 依赖

- Python 3 + Pillow（通常已安装；没有则 `pip install Pillow`）
- 仅 Windows

## 两步工作流

**当 AI 需要截取特定区域但不知道坐标时，执行以下步骤：**

### Step 1 — 侦察 (scout)

```bash
python scripts/capture.py scout <output.png>
```

生成一张缩小（默认 1/4）的全屏预览图。AI 读取这张图来确定目标区域。

### Step 2 — 精确截取

```bash
python scripts/capture.py region <x> <y> <w> <h> <output.png>
```

AI 从 scout 图识别目标位置后，指定坐标精确截取。

> 坐标推算：scout 图是 1/4 缩放，所以 scout 图中的 (a, b) → 实际 (a×4, b×4)。

## 五种模式

| 模式 | 命令 | 用途 |
|---|---|---|
| `scout` | `python scripts/capture.py scout [scale] output.png` | 侦查预览。可指定缩放比例（默认 4） |
| `full` | `python scripts/capture.py full output.png` | 全屏（所有显示器） |
| `region` | `python scripts/capture.py region x y w h output.png` | 指定矩形区域 |
| `window` | `python scripts/capture.py window "title" output.png` | 按标题匹配窗口 |
| `list` | `python scripts/capture.py list` | 列出所有可见窗口（不截图） |

## 使用场景

| 用户说 | 操作 |
|---|---|
| "截图" / "截个图" | `scout` → 读取 → 用户确认后 `full` 或 `region` |
| "截取错误弹窗" | `list` 或 `scout` → 找到目标 → `window` 或 `region` |
| "截取 Chrome 浏览器" | `window "Chrome" output.png` |
| "截取左上角那个小窗口" | `scout` → AI 读取识别 → `region x y w h` |
| "看看屏幕现在有什么" | `scout` → AI 读取后描述屏幕内容 |

## 注意事项

- **始终先 scout**：不要盲目全屏截图——先拍缩略图让 AI 定位。
- **坐标推算**：scout 默认 1/4 缩放，实际坐标 = scout 坐标 × 4。
- **DPI 缩放**：脚本已设置 system DPI awareness，坐标对应物理像素。
- **多显示器**：`full` 和 `scout` 捕获整个虚拟桌面（所有显示器）。
- **窗口匹配**：`window` 是大小写不敏感的子串匹配，匹配第一个可见窗口。
- **截图路径**：默认输出到当前工作目录，可指定路径。