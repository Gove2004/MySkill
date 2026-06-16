# 几何绘制图元库

所有 UI 和游戏单位的纯代码绘制方案。零贴图，直接复制到任意 Godot 项目。

## 通用模式

```gdscript
# Control（UI）和 Node2D（单位）都适用
extends Control  # 或 Node2D

# 1. 参数全部 @export，拖入就能调
@export var radius: float = 16.0
@export var color: Color = Color.WHITE

# 2. 不想拦截鼠标输入
func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE  # 需要点击用 STOP

# 3. _process 只更新动画参数
var _pulse_time: float = 0.0

func _process(delta: float) -> void:
    _pulse_time += delta * 3.0
    queue_redraw()

# 4. _draw 中绘制所有内容
func _draw() -> void:
    _draw_shape(center, radius, color)
```

## 几何图元大全

### 基本形状

```gdscript
# ===== 圆形（三层：光晕→主体→内核）=====
func draw_circle_glowing(center: Vector2, radius: float, color: Color) -> void:
    draw_circle(center, radius * 1.5, Color(color.r, color.g, color.b, 0.15))
    draw_circle(center, radius, color)
    draw_circle(center, radius * 0.4, color.lightened(0.4))

# ===== 正三角形（尖端朝上）=====
func draw_triangle_up(center: Vector2, r: float, c: Color) -> void:
    draw_colored_polygon(PackedVector2Array([
        center + Vector2(0, -r),
        center + Vector2(r * 0.866, r * 0.5),
        center + Vector2(-r * 0.866, r * 0.5),
    ]), c)

# ===== 倒三角形 =====
func draw_triangle_down(center: Vector2, r: float, c: Color) -> void:
    draw_colored_polygon(PackedVector2Array([
        center + Vector2(0, r),
        center + Vector2(r * 0.866, -r * 0.5),
        center + Vector2(-r * 0.866, -r * 0.5),
    ]), c)

# ===== 正方形 =====
func draw_square(center: Vector2, half: float, c: Color) -> void:
    draw_rect(Rect2(center.x - half, center.y - half, half * 2, half * 2), c)

# ===== 菱形 =====
func draw_diamond(center: Vector2, r: float, c: Color) -> void:
    draw_colored_polygon(PackedVector2Array([
        center + Vector2(0, -r), center + Vector2(r, 0),
        center + Vector2(0, r), center + Vector2(-r, 0),
    ]), c)

# ===== 正六边形 =====
func draw_hexagon(center: Vector2, r: float, c: Color, offset: float = -PI/2) -> void:
    var pts := PackedVector2Array()
    for i in range(6):
        var a: float = offset + i * TAU / 6.0
        pts.append(center + Vector2(cos(a), sin(a)) * r)
    draw_colored_polygon(pts, c)

# ===== 十字（两个交叉矩形）=====
func draw_cross(center: Vector2, arm_w: float, arm_l: float, c: Color) -> void:
    draw_rect(Rect2(center.x - arm_w, center.y - arm_l, arm_w * 2, arm_l * 2), c)
    draw_rect(Rect2(center.x - arm_l, center.y - arm_w, arm_l * 2, arm_w * 2), c)

# ===== 扇形 =====
func draw_fan(center: Vector2, r: float, start: float, end: float, seg: int, c: Color) -> void:
    var pts := PackedVector2Array([center])
    for i in range(seg + 1):
        var a: float = start + (end - start) * i / seg
        pts.append(center + Vector2(cos(a), sin(a)) * r)
    draw_colored_polygon(pts, c)

# ===== 旋转三角形（动态角度）=====
func draw_triangle_rotating(center: Vector2, r: float, angle: float, c: Color) -> void:
    var pts := PackedVector2Array()
    for i in range(3):
        var a: float = angle + i * TAU / 3.0 - PI / 2.0
        pts.append(center + Vector2(cos(a), sin(a)) * r)
    draw_colored_polygon(pts, c)
```

### 实用辅助

```gdscript
# ===== 状态条（从底部向上填充）=====
func draw_bar(pos: Vector2, w: float, h: float, ratio: float, fg: Color, bg: Color) -> void:
    var r := clampf(ratio, 0.0, 1.0)
    draw_rect(Rect2(pos.x, pos.y, w, h), bg)
    draw_rect(Rect2(pos.x, pos.y + h - h * r, w, h * r), fg)

# ===== 弧形段 =====
func draw_arc_segment(center: Vector2, r: float, start: float, end: float, c: Color, w: float = 2.0) -> void:
    draw_arc(center, r, start, end, 64, c, w)

# ===== 点阵文字（用圆点表示）=====
func draw_dot_text(start: Vector2, text: String, spacing: float, dot_radius: float, c: Color) -> void:
    for i in range(mini(text.length(), 16)):
        draw_circle(Vector2(start.x + i * spacing, start.y), dot_radius, c)

# ===== 脉动缩放值 =====
func pulse(t: float, speed: float = 2.0, amount: float = 0.05) -> float:
    return 1.0 + sin(t * speed) * amount
```

## 交互模式

```gdscript
extends Control

var _button_center: Vector2
var _button_radius: float = 20.0
var _hovered: bool = false

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_STOP

func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        _hovered = event.position.distance_to(_button_center) < _button_radius * 1.5
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        if _hovered: _on_click()

func _draw() -> void:
    var c := hover_color if _hovered else normal_color
    draw_circle(_button_center, _button_radius, c)
```

## 绘制性能参考

| 函数 | 性能 | 说明 |
|------|------|------|
| `draw_rect` | ⭐⭐⭐ 最快 | 单色矩形填充 |
| `draw_circle` | ⭐⭐⭐ 快 | 圆形，中等半径 |
| `draw_line` | ⭐⭐⭐ 快 | 直线 |
| `draw_arc` | ⭐⭐ 中等 | 段数保持≤64 |
| `draw_colored_polygon` | ⭐⭐ 中等 | 顶点数保持≤32 |
| `draw_polygon` | ⭐ 较慢 | 多色渐变，少用 |
| `draw_string` | ⭐ 较慢 | 文本，少用 |

## 状态表达通用模式

```gdscript
# 正常 → 禁用（灰色覆盖）
if _disabled:
    draw_rect(Rect2(...), Color(0.3, 0.3, 0.3, 0.8))

# 正常 → 悬停（变亮/变色）
var display_color = hover_color if _hovered else base_color

# 正常 → 受伤（闪白 + tween恢复）
_color = Color.WHITE
var tween := create_tween()
tween.tween_property(self, "_color", base_color, 0.15)

# 颜色渐变过渡
_display_color = _display_color.lerp(target_color, delta * 3.0)
```
