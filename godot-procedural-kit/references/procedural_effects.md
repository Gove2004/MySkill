# 程序化特效

使用纯几何动画实现通用视觉反馈，零贴图。所有特效通过 `Node2D` 与脚本组合实现，可作为独立模块接入项目。

## 通用模式

每个特效一个独立 `.gd` 文件，负责：
- 初始化参数
- 驱动生命周期
- 执行绘制
- 在完成后自我清理

```gdscript
extends Node2D

var speed: float = 200.0
var max_range: float = 300.0
var effect_color: Color = Color.WHITE

var _radius: float = 0.0
var _time: float = 0.0

func _ready() -> void:
    _radius = 0.0

func _process(delta: float) -> void:
    _time += delta
    _radius += speed * delta
    if _radius >= max_range:
        queue_free()
    queue_redraw()

func _draw() -> void:
    var progress: float = _radius / max_range
    var alpha: float = 1.0 - progress
    draw_arc(
        Vector2.ZERO,
        _radius,
        0,
        TAU,
        64,
        Color(effect_color.r, effect_color.g, effect_color.b, alpha),
        2.0
    )
```

## 效果类型

### 1. 扩散环（ExpandingRing）

多层圆形扩散，适合表示范围、变化、传播或脉冲反馈。

```gdscript
# expanding_ring.gd
extends Node2D

var speed: float = 200.0
var max_range: float = 300.0
var effect_color: Color = Color(0.4, 0.8, 0.9)
var width: float = 2.0
var layer_count: int = 2

var _radius: float = 0.0

func _process(delta: float) -> void:
    _radius += speed * delta
    if _radius >= max_range:
        queue_free()
    queue_redraw()

func _draw() -> void:
    var progress: float = _radius / max_range
    var alpha: float = 1.0 - progress
    for i in range(layer_count):
        var r: float = _radius - i * 8.0
        if r > 0:
            draw_arc(
                Vector2.ZERO,
                r,
                0,
                TAU,
                64,
                Color(effect_color.r, effect_color.g, effect_color.b, alpha - i * 0.2),
                width * (1.0 - i * 0.3)
            )
```

### 2. 直线高亮（Beam）

短时直线反馈，适合表示方向、连接、扫描、能量流或瞬时强调。

```gdscript
# beam.gd
extends Node2D

var beam_length: float = 600.0
var beam_width: float = 12.0
var beam_color: Color = Color(1.0, 0.6, 0.2)

var _time: float = 0.0
var _direction: Vector2 = Vector2.RIGHT

func _ready() -> void:
    if has_meta("direction"):
        _direction = get_meta("direction")

func _process(delta: float) -> void:
    _time += delta
    if _time > 0.15:
        queue_free()
    queue_redraw()

func _draw() -> void:
    var end_pos: Vector2 = _direction * beam_length
    var alpha: float = 1.0 - _time / 0.15
    draw_line(
        Vector2.ZERO,
        end_pos,
        Color(beam_color.r, beam_color.g, beam_color.b, alpha * 0.3),
        beam_width * 2.5,
        true
    )
    draw_line(
        Vector2.ZERO,
        end_pos,
        Color(beam_color.r, beam_color.g, beam_color.b, alpha),
        beam_width,
        true
    )
    draw_circle(
        Vector2.ZERO,
        6.0 * alpha,
        Color(beam_color.r, beam_color.g, beam_color.b, alpha)
    )
```

### 3. 轨迹对象（Projectile）

包含移动阶段与结束阶段的两段式效果，适合表示轨迹、抛出、指向性移动或到点展开的视觉反馈。

```gdscript
# projectile.gd
extends Node2D

var end_radius: float = 50.0
var fly_speed: float = 150.0
var max_range: float = 250.0
var color: Color = Color(0.9, 0.4, 0.1)

enum Phase { FLYING, FINISHING }
var _phase: Phase = Phase.FLYING
var _distance: float = 0.0
var _target_pos: Vector2

func _ready() -> void:
    _target_pos = position + Vector2.RIGHT * max_range
    if has_meta("target"):
        _target_pos = get_meta("target")

func _process(delta: float) -> void:
    match _phase:
        Phase.FLYING:
            var dir := (_target_pos - global_position).normalized()
            global_position += dir * fly_speed * delta
            if global_position.distance_to(_target_pos) < 10.0:
                _finish()
        Phase.FINISHING:
            _distance += 300.0 * delta
            if _distance >= end_radius:
                queue_free()
    queue_redraw()

func _finish() -> void:
    _phase = Phase.FINISHING
    _distance = 0.0

func _draw() -> void:
    match _phase:
        Phase.FLYING:
            var angle := (_target_pos - global_position).angle()
            var pts := PackedVector2Array()
            for i in range(4):
                pts.append(Vector2(cos(angle + PI / 4 + PI / 2 * i), sin(angle + PI / 4 + PI / 2 * i)) * 4.0)
            draw_colored_polygon(pts, color)
        Phase.FINISHING:
            var progress: float = _distance / end_radius
            var alpha: float = 1.0 - progress
            draw_arc(Vector2.ZERO, _distance, 0, TAU, 48, Color(color.r, color.g, color.b, alpha), 2.0)
            draw_circle(Vector2.ZERO, _distance * 0.6, Color(color.r, color.g, color.b, alpha * 0.3))
```

### 4. 扇形区域（FanArea）

扇形填充反馈，适合表示方向范围、扫描区域、覆盖区域或前向展开效果。

```gdscript
# fan_area.gd
extends Node2D

var range: float = 300.0
var angle: float = deg_to_rad(60.0)
var color: Color = Color(0.95, 0.4, 0.1)

var _direction: Vector2 = Vector2.RIGHT
var _time: float = 0.0

func _ready() -> void:
    if has_meta("direction"):
        _direction = get_meta("direction")

func _process(delta: float) -> void:
    _time += delta
    if _time > 0.3:
        queue_free()
    queue_redraw()

func _draw() -> void:
    var alpha: float = 1.0 - _time / 0.3
    var start_angle: float = _direction.angle() - angle / 2.0
    var end_angle: float = _direction.angle() + angle / 2.0
    var segs: int = 16

    var pts := PackedVector2Array([Vector2.ZERO])
    for i in range(segs + 1):
        var a: float = start_angle + (end_angle - start_angle) * i / segs
        pts.append(Vector2(cos(a), sin(a)) * range)
    draw_colored_polygon(pts, Color(color.r, color.g, color.b, alpha * 0.5))

    var inner := PackedVector2Array([Vector2.ZERO])
    for i in range(segs + 1):
        var a: float = start_angle + (end_angle - start_angle) * i / segs
        inner.append(Vector2(cos(a), sin(a)) * range * 0.5)
    draw_colored_polygon(inner, Color(1, 1, 1, alpha * 0.3))
```

## 选择建议

| 需求类型 | 推荐效果 | 说明 |
|---------|---------|------|
| 范围或传播 | ExpandingRing | 用半径变化表达传播感 |
| 方向或连接 | Beam | 用直线与高亮表达方向性 |
| 轨迹与落点 | Projectile | 用两段式生命周期表达过程与结束 |
| 区域覆盖 | FanArea | 用扇形表示方向范围 |
| 补充粒子反馈 | GeometricParticleEmitter | 详见 `particle_system.md` |

## 使用原则

- 一个效果脚本只负责一种清晰的视觉语义
- 生命周期应内聚在效果对象内部
- 参数命名优先表达视觉语义，而不是绑定业务对象
- 如果一个效果频繁复用，应做成独立模块而不是内联绘制
- 如果需要更强反馈，可组合多个基础效果，而不是把所有逻辑堆进单个脚本
