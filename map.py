import random
import pygame
from collections import deque

# 地图常量
TILE_EMPTY = 0
TILE_WALL = 1
TILE_STAIRS = 5
TILE_SIZE = 16

# 固定走廊宽度
CORRIDOR_WIDTH = 3  # 固定走廊宽度为3格

# 三种房间尺寸
ROOM_SIZES = [
    (9, 12),  # 小房间：走廊宽度的3-4倍
    (13, 18),  # 中房间：走廊宽度的4-6倍
    (19, 24)  # 大房间：走廊宽度的6-8倍
]


def generate_dungeon(width, height, rooms_min=6, rooms_max=16):
    """
    生成随机地牢地图，固定走廊宽度，三种房间尺寸
    """
    num_room_side = 4
    size_room_container = 32

    rooms_max = min(rooms_max, 16)
    rooms_min = max(rooms_min, 4)

    # 初始化房间网格
    room_map = [[{
        "is_valid": False,
        "x": 0, "y": 0, "width": 0, "height": 0,
        "grid_x": x, "grid_y": y
    } for x in range(num_room_side)] for y in range(num_room_side)]

    # 随机生成房间（三种尺寸）
    for y in range(num_room_side):
        for x in range(num_room_side):
            if random.random() < 0.7:
                # 随机选择一种房间尺寸
                size_type = random.choice(ROOM_SIZES)
                room_width = random.randint(size_type[0], size_type[1])
                room_height = random.randint(size_type[0], size_type[1])

                room_x = x * size_room_container + (size_room_container - room_width) // 2
                room_y = y * size_room_container + (size_room_container - room_height) // 2

                if room_x + room_width < width and room_y + room_height < height:
                    room_map[y][x].update({
                        "is_valid": True,
                        "x": room_x,
                        "y": room_y,
                        "width": room_width,
                        "height": room_height
                    })

    # 保证至少有 rooms_min 个房间
    valid_rooms = [room for row in room_map for room in row if room["is_valid"]]
    attempts = 0
    max_attempts = 100  # 最大尝试次数

    while len(valid_rooms) < rooms_min and attempts < max_attempts:
        attempts += 1
        rx = random.randint(0, num_room_side - 1)
        ry = random.randint(0, num_room_side - 1)

        if not room_map[ry][rx]["is_valid"]:
            size_type = random.choice(ROOM_SIZES)
            rw = random.randint(size_type[0], size_type[1])
            rh = random.randint(size_type[0], size_type[1])
            room_x = rx * size_room_container + (size_room_container - rw) // 2
            room_y = ry * size_room_container + (size_room_container - rh) // 2

            # 确保房间在地图边界内
            if (room_x >= 0 and room_y >= 0 and
                    room_x + rw < width and room_y + rh < height):
                room_map[ry][rx].update({
                    "is_valid": True,
                    "x": room_x,
                    "y": room_y,
                    "width": rw,
                    "height": rh
                })
                valid_rooms = [r for row in room_map for r in row if r["is_valid"]]

    # 如果还是没有足够房间，强制生成（使用小房间）
    if len(valid_rooms) < rooms_min:
        for ry in range(num_room_side):
            for rx in range(num_room_side):
                if len(valid_rooms) >= rooms_min:
                    break
                if not room_map[ry][rx]["is_valid"]:
                    # 使用最小房间尺寸确保能放入
                    rw = ROOM_SIZES[0][0]  # 最小房间宽度
                    rh = ROOM_SIZES[0][0]  # 最小房间高度
                    room_x = rx * size_room_container + (size_room_container - rw) // 2
                    room_y = ry * size_room_container + (size_room_container - rh) // 2

                    if (room_x >= 0 and room_y >= 0 and
                            room_x + rw < width and room_y + rh < height):
                        room_map[ry][rx].update({
                            "is_valid": True,
                            "x": room_x,
                            "y": room_y,
                            "width": rw,
                            "height": rh
                        })
                        valid_rooms = [r for row in room_map for r in row if r["is_valid"]]

    # 初始化地图为墙
    dungeon = [[TILE_WALL for _ in range(width)] for _ in range(height)]

    # 验证是否有足够的房间
    if len(valid_rooms) == 0:
        # 紧急情况：强制在地图中心创建一个房间
        center_room = {
            "is_valid": True,
            "x": width // 2 - 10,
            "y": height // 2 - 10,
            "width": 20,
            "height": 20,
            "grid_x": 1,
            "grid_y": 1
        }
        valid_rooms = [center_room]

    # 绘制房间
    for room in valid_rooms:
        for iy in range(room["y"], room["y"] + room["height"]):
            for ix in range(room["x"], room["x"] + room["width"]):
                if 0 <= ix < width and 0 <= iy < height:
                    dungeon[iy][ix] = TILE_EMPTY

    # 挖掘走廊函数（固定宽度，平滑转角）
    def carve_path(x1, y1, x2, y2):
        """挖掘固定宽度的L型走廊，处理平滑转角"""
        half_width = CORRIDOR_WIDTH // 2

        if random.choice([True, False]):
            # 路径1：先水平后垂直
            # 水平段
            sx, ex = min(x1, x2), max(x1, x2)
            for x in range(sx, ex + 1):
                for dy in range(-half_width, half_width + 1):
                    yy = y1 + dy
                    if 0 <= x < width and 0 <= yy < height:
                        dungeon[yy][x] = TILE_EMPTY

            # 垂直段
            sy, ey = min(y1, y2), max(y1, y2)
            for y in range(sy, ey + 1):
                for dx in range(-half_width, half_width + 1):
                    xx = x2 + dx
                    if 0 <= xx < width and 0 <= y < height:
                        dungeon[y][xx] = TILE_EMPTY

            # 填充转角区域（确保转角平滑连接）
            corner_x, corner_y = x2, y1
            for dy in range(-half_width, half_width + 1):
                for dx in range(-half_width, half_width + 1):
                    cx = corner_x + dx
                    cy = corner_y + dy
                    if 0 <= cx < width and 0 <= cy < height:
                        dungeon[cy][cx] = TILE_EMPTY
        else:
            # 路径2：先垂直后水平
            # 垂直段
            sy, ey = min(y1, y2), max(y1, y2)
            for y in range(sy, ey + 1):
                for dx in range(-half_width, half_width + 1):
                    xx = x1 + dx
                    if 0 <= xx < width and 0 <= y < height:
                        dungeon[y][xx] = TILE_EMPTY

            # 水平段
            sx, ex = min(x1, x2), max(x1, x2)
            for x in range(sx, ex + 1):
                for dy in range(-half_width, half_width + 1):
                    yy = y2 + dy
                    if 0 <= x < width and 0 <= yy < height:
                        dungeon[yy][x] = TILE_EMPTY

            # 填充转角区域
            corner_x, corner_y = x1, y2
            for dy in range(-half_width, half_width + 1):
                for dx in range(-half_width, half_width + 1):
                    cx = corner_x + dx
                    cy = corner_y + dy
                    if 0 <= cx < width and 0 <= cy < height:
                        dungeon[cy][cx] = TILE_EMPTY

    # 获取房间中心点（地砖坐标）
    centers = [(r["x"] + r["width"] // 2, r["y"] + r["height"] // 2) for r in valid_rooms]
    if not centers:
        return dungeon, [], {}, []

    # 使用 MST 连接所有房间
    random.shuffle(centers)
    connected = [centers[0]]
    unconnected = centers[1:]

    while unconnected:
        target = unconnected.pop(0)
        nearest = min(connected, key=lambda c: (c[0] - target[0]) ** 2 + (c[1] - target[1]) ** 2)
        carve_path(nearest[0], nearest[1], target[0], target[1])
        connected.append(target)

    # 清理死胡同走廊（只连接一个房间的走廊段）
    def remove_dead_ends():
        """移除死胡同走廊"""
        changed = True
        iterations = 0
        max_iterations = 50  # 防止无限循环

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    # 只处理走廊（非房间内的地板）
                    if dungeon[y][x] == TILE_EMPTY:
                        # 检查是否在房间内
                        in_room = False
                        for room in valid_rooms:
                            if (room["x"] <= x < room["x"] + room["width"] and
                                    room["y"] <= y < room["y"] + room["height"]):
                                in_room = True
                                break

                        # 如果不在房间内，检查相邻可通行格子数
                        if not in_room:
                            neighbors = 0
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    if dungeon[ny][nx] == TILE_EMPTY:
                                        neighbors += 1

                            # 如果只有1个或0个邻居，说明是死胡同，删除
                            if neighbors <= 1:
                                dungeon[y][x] = TILE_WALL
                                changed = True

    # 执行死胡同清理
    remove_dead_ends()

    # 构建房间中心列表（含房间对象）
    room_centers_grid = []
    for r in valid_rooms:
        cx = r["x"] + r["width"] // 2
        cy = r["y"] + r["height"] // 2
        room_centers_grid.append((cx, cy, r))

    # 使用BFS判断两点是否可达
    def bfs_connected(dng, w, h, x1, y1, x2, y2):
        """BFS检查两点是否通过TILE_EMPTY连通"""
        if not (0 <= x1 < w and 0 <= y1 < h and 0 <= x2 < w and 0 <= y2 < h):
            return False
        if dng[y1][x1] != TILE_EMPTY or dng[y2][x2] != TILE_EMPTY:
            return False

        visited = [[False] * w for _ in range(h)]
        queue = deque([(x1, y1)])
        visited[y1][x1] = True

        while queue:
            x, y = queue.popleft()
            if x == x2 and y == y2:
                return True

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if not visited[ny][nx] and dng[ny][nx] == TILE_EMPTY:
                        visited[ny][nx] = True
                        queue.append((nx, ny))
        return False

    # 构建房间之间的连接图
    graph = {i: [] for i in range(len(valid_rooms))}
    for i in range(len(valid_rooms)):
        for j in range(i + 1, len(valid_rooms)):
            cx1, cy1 = room_centers_grid[i][0], room_centers_grid[i][1]
            cx2, cy2 = room_centers_grid[j][0], room_centers_grid[j][1]
            if bfs_connected(dungeon, width, height, cx1, cy1, cx2, cy2):
                graph[i].append(j)
                graph[j].append(i)

    return dungeon, valid_rooms, graph, room_centers_grid


class Map:
    """地牢地图类"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        result = generate_dungeon(width, height)
        if not result or len(result[1]) == 0:
            raise RuntimeError("Failed to generate any valid rooms")

        self.tiles, self.rooms, self.room_graph, self.room_centers_grid = result
        self.start_room_index = None
        self.player_position = self.find_start_position()
        self.room_centers = self.find_all_room_centers()

    def find_start_position(self):
        """选择边缘房间作为起始点"""
        edge_rooms = [r for r in self.rooms if r["grid_x"] in [0, 3] or r["grid_y"] in [0, 3]]
        start_room = random.choice(edge_rooms) if edge_rooms else self.rooms[0]
        self.start_room_index = self.rooms.index(start_room)

        cx = start_room["x"] + start_room["width"] // 2
        cy = start_room["y"] + start_room["height"] // 2
        px = cx * TILE_SIZE + TILE_SIZE // 2
        py = cy * TILE_SIZE + TILE_SIZE // 2
        return (px, py)

    def find_all_room_centers(self):
        """获取所有房间中心的像素坐标"""
        centers = []
        for r in self.rooms:
            if r["is_valid"]:
                gx = r["x"] + r["width"] // 2
                gy = r["y"] + r["height"] // 2
                if 0 <= gx < self.width and 0 <= gy < self.height:
                    px = gx * TILE_SIZE + TILE_SIZE // 2
                    py = gy * TILE_SIZE + TILE_SIZE // 2
                    centers.append((px, py))
        return centers

    def is_passable(self, x, y):
        """检测像素坐标是否可通行"""
        tx = int(x // TILE_SIZE)
        ty = int(y // TILE_SIZE)
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return False
        tile = self.tiles[ty][tx]
        return tile == TILE_EMPTY

    def get_room_centers(self):
        """返回所有房间中心像素坐标"""
        return self.room_centers

    def render(self, screen, camera_x, camera_y):
        """渲染地图（完整渲染，无黑色虚空）"""
        # 计算屏幕可见区域对应的地砖范围
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        # 计算起始和结束地砖坐标（扩大范围确保完整显示）
        start_x = max(0, int(camera_x // TILE_SIZE) - 2)
        start_y = max(0, int(camera_y // TILE_SIZE) - 2)
        end_x = min(self.width, int((camera_x + screen_w) // TILE_SIZE) + 3)
        end_y = min(self.height, int((camera_y + screen_h) // TILE_SIZE) + 3)

        # 配色方案
        FLOOR_COLOR = (200, 200, 200)  # 浅灰地板
        WALL_COLOR = (50, 50, 50)  # 深灰墙

        # 渲染所有可见地砖
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                color = FLOOR_COLOR if tile == TILE_EMPTY else WALL_COLOR

                rect = pygame.Rect(
                    x * TILE_SIZE - camera_x,
                    y * TILE_SIZE - camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(screen, color, rect)

        # 填充屏幕外的区域为墙壁颜色（防止黑色虚空）
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        # 填充四边界外
        if camera_x < 0:
            pygame.draw.rect(screen, WALL_COLOR, (0, 0, -camera_x, screen_h))

        if camera_y < 0:
            pygame.draw.rect(screen, WALL_COLOR, (0, 0, screen_w, -camera_y))

        map_pixel_w = self.width * TILE_SIZE
        right_edge = map_pixel_w - camera_x
        if right_edge < screen_w:
            pygame.draw.rect(screen, WALL_COLOR, (right_edge, 0, screen_w - right_edge, screen_h))

        map_pixel_h = self.height * TILE_SIZE
        bottom_edge = map_pixel_h - camera_y
        if bottom_edge < screen_h:
            pygame.draw.rect(screen, WALL_COLOR, (0, bottom_edge, screen_w, screen_h - bottom_edge))