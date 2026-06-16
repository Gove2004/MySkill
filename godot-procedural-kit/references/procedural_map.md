# 程序化地图生成

网格化随机地图算法，适用于需要程序化生成地形的游戏（塔防、RTS、策略等）。

## 核心概念

基于网格（Grid）的简单地图生成：
1. 初始化 N×M 网格，全部可通行
2. 按密度随机填充障碍
3. 四方向走廊保证关键路径连通
4. BFS 验证连通性，不连通则强制打通

```gdscript
# 核心算法（语言无关，任何引擎可移植）
# 网格: 0=可通行, 1=障碍

func generate():
    # 1. 随机填充
    for x in range(cols):
        for y in range(rows):
            if randf() < density and not is_near_center(x, y):
                grid[y][x] = 1

    # 2. 切走廊（从四边入口到中心）
    for entry in [top, bottom, left, right]:
        carve_path(entry, center)

    # 3. BFS 验证
    validate_connectivity()

# 走廊切割：从 A 到 B，宽至少 2 格
func carve_path(from, to):
    while current != to:
        clear_around(current, radius=1)  # 清3x3区域
        # 优先朝坐标差大的方向走
        diff = to - current
        if abs(diff.x) > abs(diff.y):
            current.x += sign(diff.x)
        else:
            current.y += sign(diff.y)
        # 30%概率随机偏转（使走廊弯曲自然）

# BFS 连通性验证
func validate_connectivity():
    visited = bfs_from(center)
    for entry in [top, bottom, left, right]:
        if not visited[entry]:
            force_clear_path(entry, center)
            validate_connectivity()  # 递归
            return
```

## Godot 实现要点

```gdscript
# === 网格数据 ===
var _grid: PackedByteArray  # 1D 数组模拟 2D: grid[y*cols+x]
var _grid_size: float = 64.0  # 像素/格

func is_blocked(grid_pos: Vector2i) -> bool:
    return _grid[grid_pos.y * _cols + grid_pos.x] == 1

func world_to_grid(pos: Vector2) -> Vector2i:
    return Vector2i(int(pos.x / _grid_size), int(pos.y / _grid_size))

func grid_to_world(pos: Vector2i) -> Vector2:
    return Vector2(pos.x * _grid_size + _grid_size/2, pos.y * _grid_size + _grid_size/2)

# === 碰撞体生成 ===
# 为每个障碍格创建 StaticBody2D + CollisionShape2D (RectangleShape2D)
func _spawn_collisions() -> void:
    for y in range(_rows):
        for x in range(_cols):
            if _grid[y*_cols+x] != 1: continue
            var body := StaticBody2D.new()
            body.position = grid_to_world(Vector2i(x, y))
            var shape := CollisionShape2D.new()
            var rect := RectangleShape2D.new()
            rect.size = Vector2(_grid_size * 0.9, _grid_size * 0.9)
            shape.shape = rect
            body.add_child(shape)
            add_child(body)

# === 视觉绘制 ===
func _draw() -> void:
    for vis in _visuals:
        var p: Vector2 = vis["pos"] - global_position
        var s: Vector2 = vis["size"]
        draw_rect(Rect2(p - s*0.5, s), vis["color"])
```

## Flow Field 寻路（可选）

在网格基础上做 BFS 寻路，所有单位 O(1) 查询：

```gdscript
# 从目标点 BFS 扩散，记录每格到目标的 cost
# 每格方向 = 指向邻居中 cost 最小的那格

func recalculate():
    # BFS 从基地格扩散
    var queue = [base_index]
    costs[base_index] = 0
    while queue:
        var idx = queue.pop_front()
        for neighbor in four_directions(idx):
            if costs[neighbor] == -1:  # 未访问
                costs[neighbor] = costs[idx] + 1
                queue.append(neighbor)

    # 计算方向：看 8 邻居中 cost 最小的
    for y in range(rows):
        for x in range(cols):
            directions[y*cols+x] = best_direction(x, y)

# 单位查询：每帧取方向向量
func get_direction(world_pos: Vector2) -> Vector2:
    var gx := int(world_pos.x / grid_size)
    var gy := int(world_pos.y / grid_size)
    return directions[clampi(gy,0,rows-1)*cols + clampi(gx,0,cols-1)]
```

## 参数调优

| 参数 | 说明 | 建议 |
|------|------|------|
| `_grid_size` | 每格像素大小 | 64（匹配常用 tile 尺寸） |
| `density` | 障碍密度 0~1 | 0.25 开局不拥挤 |
| `corridor_width` | 走廊宽度（格数） | 2 格 |
| `clear_radius` | 起点周围清空半径 | 3 格 |
| `random_wobble` | 走廊随机偏转概率 | 0.3 让走廊看起来自然 |
