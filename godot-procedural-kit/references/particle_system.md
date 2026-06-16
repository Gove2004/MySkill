# 程序化粒子系统

自包含的几何粒子方案，零贴图，适合表示命中、强调、切换、生成、消散等视觉反馈。

## 粒子发射器

```gdscript
# geometric_particle_emitter.gd
class_name GeometricParticleEmitter
extends Node2D

enum Shape { CIRCLE, TRIANGLE, RECTANGLE }

@export var particle_count: int = 8
@export var shape: Shape = Shape.CIRCLE
@export var color: Color = Color.WHITE
@export var min_speed: float = 40.0
@export var max_speed: float = 120.0
@export var min_size: float = 2.0
@export var max_size: float = 5.0
@export var lifetime: float = 0.5
@export var fade: bool = true
@export var gravity: Vector2 = Vector2.ZERO

var _particles: Array[Dictionary] = []
var _active: bool = false

# ===== 调用方式 =====
# var e := GeometricParticleEmitter.new()
# e.global_position = pos
# e.particle_count = 12
# e.shape = GeometricParticleEmitter.Shape.CIRCLE  # CIRCLE/TRIANGLE/RECTANGLE
# e.color = Color.RED
# get_tree().current_scene.add_child(e)
# e.emit()

func emit() -> void:
    _particles.clear()
    for i in range(particle_count):
        var angle: float = randf() * TAU
        var speed: float = randf_range(min_speed, max_speed)
        _particles.append({
            "pos": Vector2.ZERO,
            "vel": Vector2(cos(angle), sin(angle)) * speed,
            "size": randf_range(min_size, max_size),
            "life": lifetime,
            "max_life": lifetime,
        })
    _active = true

func _process(delta: float) -> void:
    if not _active: return
    var all_dead := true
    for p in _particles:
        p["life"] -= delta
        if p["life"] > 0.0:
            all_dead = false
            p["vel"] += gravity * delta
            p["pos"] += p["vel"] * delta
    queue_redraw()
    if all_dead: queue_free()

func _draw() -> void:
    if not _active: return
    for p in _particles:
        if p["life"] <= 0.0: continue
        var ratio: float = p["life"] / p["max_life"]
        var c := Color(color.r, color.g, color.b, ratio if fade else 1.0)
        var s: float = p["size"] * ratio
        match shape:
            Shape.CIRCLE:   draw_circle(p["pos"], s, c)
            Shape.TRIANGLE: draw_colored_polygon([
                p["pos"]+Vector2(0,-s), p["pos"]+Vector2(s*0.866,s*0.5), p["pos"]+Vector2(-s*0.866,s*0.5)], c)
            Shape.RECTANGLE:draw_rect(Rect2(p["pos"]-Vector2(s,s)*0.5, Vector2(s,s)), c)
```

## 帧分摊队列

防止大量单位同帧死亡导致卡顿。

```gdscript
# death_effect_queue.gd
class_name EffectQueue

const MAX_PER_FRAME: int = 3

static var _queue: Array[Dictionary] = []
static var _tree: SceneTree = null

static func enqueue(config: Dictionary, tree: SceneTree) -> void:
    if _tree == null: _tree = tree
    _queue.append(config)

# 主循环每帧调用 EffectQueue.process_queue()
static func process_queue() -> void:
    var count: int = mini(_queue.size(), MAX_PER_FRAME)
    for i in range(count):
        var cfg: Dictionary = _queue.pop_front()
        _spawn(cfg)

static func _spawn(cfg: Dictionary) -> void:
    var emitter := GeometricParticleEmitter.new()
    emitter.global_position = cfg.get("position", Vector2.ZERO)
    emitter.particle_count = cfg.get("particle_count", 8)
    emitter.shape = cfg.get("shape", GeometricParticleEmitter.Shape.CIRCLE)
    emitter.color = cfg.get("color", Color.WHITE)
    emitter.min_speed = cfg.get("min_speed", 25.0)
    emitter.max_speed = cfg.get("max_speed", 80.0)
    emitter.min_size = cfg.get("min_size", 2.0)
    emitter.max_size = cfg.get("max_size", 4.0)
    emitter.lifetime = cfg.get("lifetime", 0.4)
    _tree.current_scene.add_child(emitter)
    emitter.emit()
```

## 镜头震动

```gdscript
# camera_shake.gd
class_name CameraShake

static func shake(camera: Camera2D, intensity: float = 5.0, duration: float = 0.2) -> void:
    if not is_instance_valid(camera): return
    var tween := camera.create_tween()
    var steps: int = int(duration / 0.03)
    for i in range(steps):
        var decay: float = 1.0 - float(i) / float(steps)
        var offset := Vector2(randf_range(-intensity, intensity), randf_range(-intensity, intensity)) * decay
        tween.tween_property(camera, "offset", offset, 0.03)
    tween.tween_property(camera, "offset", Vector2.ZERO, 0.03)  # 归零
```
