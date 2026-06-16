# 程序化音效

使用 gdfxr 插件在运行时生成音效，适用于低资源依赖、快速迭代和可参数化音效方案。

## 前置依赖

- 在项目 `addons/` 目录安装 gdfxr 插件
- 确认插件文件可被项目引用
- 在项目设置中启用插件
- 若使用全局音频管理器，需在项目中注册相应 Autoload；若不想依赖额外全局对象，可使用场景内管理器或本地播放器池

## 运行时 SFX 管理器

如果不想依赖额外的全局管理对象，可以在主场景或音频系统节点上挂一个管理器，内部维护 `AudioStreamPlayer` 池。

```gdscript
# sfx_manager.gd
extends Node

const SFXRConfig = preload("res://addons/gdfxr/SFXRConfig.gd")
const SFXRGenerator = preload("res://addons/gdfxr/SFXRGenerator.gd")

const MAX_PLAYERS: int = 8
var _cache: Dictionary = {}
var _players: Array[AudioStreamPlayer] = []

func _ready() -> void:
    for i: int in range(MAX_PLAYERS):
        var player := AudioStreamPlayer.new()
        add_child(player)
        _players.append(player)

func play(name: StringName) -> void:
    _play(name)

func _play(name: StringName) -> void:
    var stream: AudioStreamWAV = _get_stream(name)
    if stream == null:
        return
    for player: AudioStreamPlayer in _players:
        if not player.playing:
            player.stream = stream
            player.play()
            return

func _get_stream(name: StringName) -> AudioStreamWAV:
    if _cache.has(name):
        return _cache[name]

    var config := SFXRConfig.new()
    config.randomize_in_category(SFXRConfig.Category.LASER_SHOOT)
    var generator := SFXRGenerator.new()
    var stream: AudioStreamWAV = generator.generate_audio_stream(config)
    _cache[name] = stream
    return stream
```

适合场景：
- 运行时需要生成少量离散音效
- 需要避免预制音频文件
- 希望音效调用集中管理

## 程序化音效库

如果希望每种音效可复现、可缓存、可参数化，可以使用一个声音库来统一管理。

```gdscript
# sfx_library.gd
class_name SfxLibrary

const _SFXRConfig = preload("res://addons/gdfxr/SFXRConfig.gd")
const _SFXRGenerator = preload("res://addons/gdfxr/SFXRGenerator.gd")

const MAX_CONCURRENT: int = 8
const MIN_INTERVAL: float = 0.06
static var _timestamps: Array = []
static var _last_play: Dictionary = {}
static var _cache: Dictionary = {}

const SOUND_MAP: Dictionary = {
    &"pickup":      [0, 100],
    &"action":      [1, 200],
    &"impact":      [2, 300],
    &"alert":       [3, 400],
    &"upgrade":     [4, 500],
    &"confirm":     [5, 600],
    &"click":       [6, 700],
    &"hover":       [6, 111],
    &"success":     [0, 800],
    &"failure":     [3, 900],
}

static func get_sfx(name: StringName) -> AudioStreamWAV:
    if _cache.has(name):
        return _cache[name]
    if not SOUND_MAP.has(name):
        return null

    var mapping: Array = SOUND_MAP[name]
    seed(mapping[1])
    var config = _SFXRConfig.new()
    config.randomize_in_category(mapping[0])

    match name:
        &"impact":
            config.wave_type = 3
            config.p_base_freq = 0.07
            config.p_env_decay = 0.5
            config.p_env_punch = 0.7
        &"alert":
            config.p_freq_ramp = -0.3

    var gen = _SFXRGenerator.new()
    var stream: AudioStreamWAV = gen.generate_audio_stream(config)
    randomize()
    _cache[name] = stream
    return stream

static func play(name: StringName) -> void:
    var now: float = Time.get_ticks_msec() / 1000.0
    _timestamps = _timestamps.filter(func(t): return now - t < 0.35)
    if _timestamps.size() >= MAX_CONCURRENT:
        return
    if _last_play.has(name) and now - _last_play[name] < MIN_INTERVAL:
        return

    var stream := get_sfx(name)
    if stream:
        _timestamps.append(now)
        _last_play[name] = now
        SoundManager.play_sound(stream, "SFX")
```

## 背景音乐管理器

```gdscript
# bgm_manager.gd
class_name BgmManager

static var _player: AudioStreamPlayer = null
static var _volume_db: float = 0.0
static var _tree: SceneTree = null

static func play(stream: AudioStream, fade_in: float = 0.5) -> void:
    if stream == null:
        return
    _ensure_player()
    if _player.stream == stream and _player.playing:
        return
    _player.stream = stream
    if fade_in > 0.0:
        _player.volume_db = -80.0
        _player.play()
        _tree.create_tween().tween_property(_player, "volume_db", _volume_db, fade_in)
    else:
        _player.volume_db = _volume_db
        _player.play()

static func stop(fade_out: float = 0.5) -> void:
    if _player == null or not _player.playing:
        return
    if fade_out > 0.0:
        var tween := _tree.create_tween()
        tween.tween_property(_player, "volume_db", -80.0, fade_out)
        tween.tween_callback(_player.stop)
    else:
        _player.stop()

static func crossfade(new_stream: AudioStream, dur: float = 1.0) -> void:
    if new_stream == null:
        return
    _ensure_player()
    var half: float = dur * 0.5
    if _player.playing:
        var tween := _tree.create_tween()
        tween.tween_property(_player, "volume_db", -80.0, half)
        tween.tween_callback(func(): _player.stream = new_stream; _player.play())
        tween.tween_property(_player, "volume_db", _volume_db, half)
    else:
        play(new_stream, half)

static func set_volume(db: float) -> void:
    _volume_db = db
    if _player and _player.playing:
        _player.volume_db = _volume_db

static func is_playing() -> bool:
    return _player != null and _player.playing

static func _ensure_player() -> void:
    if _player != null and is_instance_valid(_player):
        return
    _tree = Engine.get_main_loop() as SceneTree
    if _tree == null:
        return
    _player = AudioStreamPlayer.new()
    _player.bus = "Master"
    _player.volume_db = _volume_db
    _tree.root.add_child(_player)
```

## 参数说明

常见可调项：
- `p_base_freq`：基频
- `p_freq_ramp`：音高变化方向
- `p_env_attack`：起音时间
- `p_env_sustain`：持续时间
- `p_env_decay`：衰减时间
- `p_env_punch`：冲击感
- `wave_type`：波形类型

## 使用原则

- 音效调用应尽量集中
- 高频触发应做节流
- 稳定复现优先于完全随机
- 如果最终项目有专业音频资产，可把程序化音效作为原型或占位方案

## 注意事项

- 程序化音效适合快速验证和低依赖方案
- 它不必替代最终音频制作流程
- 如果项目已有音频系统，应尽量复用现有结构，而不是重复造一套全局管理器
