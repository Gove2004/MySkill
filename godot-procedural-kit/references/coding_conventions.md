# 编码约定与最佳实践

适用于程序化 Godot 项目的通用编码模式。

## 场景树与坐标系预检

在以脚本和运行时生成内容为主的 Godot 项目里，先确认下面几项，能减少大量调试时间。

### Camera2D 基准

```gdscript
func _ready() -> void:
    var view_size: Vector2 = get_viewport_rect().size
    $Camera2D.current = true
    $Camera2D.global_position = view_size * 0.5
```

适用条件：
- 项目启用了 `Camera2D`
- 世界内容按视口尺寸或中心点布局

如果视觉内容整体偏移到角落，先检查相机位置与坐标系假设是否一致。

### UI 层级与路径一致性

```gdscript
# Main
# ├── Camera2D
# └── UILayer
#     └── MainUI

@onready var main_ui: Control = $UILayer/MainUI
```

如果 UI 节点改了父级或层级，必须同步更新路径引用。  
当路径容易变化时，优先考虑：
- 导出节点引用
- 依赖注入
- 更稳定的查找方式

### 运行时生成节点的顺序

```gdscript
var instance := Node2D.new()
instance.set_script(RuntimeScript)
add_child(instance)
_apply_runtime_config(instance)
```

如果先改属性再 `add_child()`，可能被 `_ready()` 中的默认值覆盖。  
对运行时创建的视觉对象、临时节点、UI 节点和效果节点都成立。

## GDScript 类型推断

Godot 4.x 在 `Variant`、`Dictionary`、动态数组和 group 查询较多的脚本里，类型推断容易变脆。

下面这些位置建议优先显式标注：

```gdscript
for p: Dictionary in _particles:
    var life: float = p["life"]

for node: Node2D in get_tree().get_nodes_in_group("targets"):
    pass

for j: int in range(10):
    var angle_step: float = angle + j * TAU / 10.0 - PI / 2.0

var flicker: float = abs(sin(_time * 1.5)) * 0.6 + 0.4
```

高风险位置：
- `Array[Dictionary]` 遍历
- `get_nodes_in_group()` 返回值遍历
- `var x :=` 接复杂表达式
- 混合字典取值、三角函数和浮点计算的中间变量

## 绘制优化

### 节流重绘

```gdscript
# 不推荐：每帧重绘
func _process(delta: float) -> void:
    queue_redraw()

# 推荐：节流 + 脏标记
var _redraw_counter: int = 0
var _visual_dirty: bool = false

func _process(delta: float) -> void:
    _redraw_counter += 1
    if _visual_dirty or _redraw_counter % 3 == 0:
        _visual_dirty = false
        queue_redraw()

func mark_visual_dirty() -> void:
    _visual_dirty = true
```

### 颜色过渡

```gdscript
_display_color = _display_color.lerp(target_color, delta * 3.0)
```

相比硬切换，插值更适合状态变化、强调反馈和过渡动画。

### 闪白/高亮反馈

```gdscript
_color = Color(1.0, 1.0, 1.0, 1.0)
queue_redraw()
var tween := create_tween()
tween.tween_property(self, "_color", base_color, 0.15)
```

适用于：
- 命中反馈
- 选中反馈
- 状态切换反馈
- 短时强调

## 通用色板原则

不要把颜色常量绑定到具体叙事对象，优先按语义命名。

```gdscript
const PRIMARY := Color(0.3, 0.75, 0.9)
const DANGER := Color(0.85, 0.15, 0.15)
const SUCCESS := Color(0.2, 0.8, 0.3)
const WARNING := Color(1.0, 0.85, 0.2)
const EMPHASIS := Color(1.0, 0.85, 0.4)
const DISABLED := Color(0.3, 0.3, 0.3)
const SURFACE := Color(0.05, 0.06, 0.12)
const ACCENT := Color(0.4, 0.8, 0.9)
```

常用颜色操作：

```gdscript
color.lightened(0.3)
color.darkened(0.2)
Color(c.r, c.g, c.b, a)
color.lerp(other, t)
```

## Tween 动画模式

```gdscript
var tween := create_tween()
node.scale = Vector2(1.3, 1.3)
tween.tween_property(node, "scale", Vector2(1.0, 1.0), 0.2)\
    .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
```

```gdscript
tween.tween_property(camera, "position", target_pos, 0.4)\
    .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
```

```gdscript
tween.tween_property(node, "modulate:a", 1.0, 0.5)\
    .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
```

```gdscript
tween.tween_property(rect, "modulate:a", 0.0, 0.3)
tween.tween_callback(func(): rect.texture = new_texture)
tween.tween_property(rect, "modulate:a", 1.0, 0.3)
```

## Input 处理模式

```gdscript
func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            _on_click()
```

```gdscript
func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed:
        match event.keycode:
            KEY_SPACE: _do_something()
            KEY_ESCAPE: _do_escape()
```

选择原则：
- 节点区域内交互，用 `_gui_input`
- 全局输入或未消费输入，用 `_unhandled_input`

## 性能注意事项

- `draw_circle` / `draw_rect` / `draw_line`：开销较低
- `draw_arc`：控制段数，通常保持在 32–64
- `draw_colored_polygon`：控制顶点数，复杂形状要注意尺寸下限
- 粒子发射器：控制单次生成量和同时活跃数量
- `get_nodes_in_group()`：不要高频无节制调用
- 运行时创建的短命对象：要注意总量、生命周期和回收时机

## 状态与计数收口

如果项目存在“对象数量驱动后续逻辑”的情况，不要只在单一出口更新计数。

```gdscript
signal finished
signal removed

func remove_self() -> void:
    removed.emit()
    queue_free()
```

```gdscript
node.finished.connect(_on_node_finished)
node.removed.connect(_on_node_removed)
```

创建、完成、超时、离场、主动移除等路径，应该统一进入同一套状态或计数体系。

## 最小可用结构建议

```text
scripts/
├── components/
│   ├── geometric_particle_emitter.gd
│   └── camera_shake.gd
├── systems/
│   ├── sfx_library.gd
│   └── runtime_registry.gd
├── effects/
│   └── reusable_effect.gd
└── ui/
    └── custom_components/
```

这只是通用起点，不应被视为固定模板。根据项目规模、依赖和复用需求裁剪即可。
