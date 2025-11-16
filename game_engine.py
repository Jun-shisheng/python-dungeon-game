import pygame
import sys
import random
import math
from collections import deque
from map import Map, TILE_EMPTY, TILE_WALL, TILE_STAIRS
from character import Player


class GameEngine:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.state = "game"
        self.victory = False
        self.move_speed = 5  # 丝滑移动速度

        # 初始化玩家和地图
        self.player = Player("勇者")
        self.map = Map(120, 80)
        self.player.x, self.player.y = self.map.player_position

        # 获取所有房间中心
        self.room_centers = self.map.get_room_centers()

        # 设置起点和终点
        if len(self.room_centers) >= 2:
            self.start_room = self._find_closest_room_center(self.player.x, self.player.y)

            # 使用路径距离而非空间距离选择终点
            farthest_room, path_distance = self._find_farthest_room_by_path(
                (self.player.x, self.player.y)
            )

            if farthest_room and farthest_room != self.start_room:
                self.end_room = farthest_room
                print(f"终点设置完成 - 路径距离: {int(path_distance)}")
            else:
                # 回退方案：使用空间距离最远的房间
                max_distance = -1
                self.end_room = self.start_room
                for center in self.room_centers:
                    if center != self.start_room:
                        dist = self._manhattan_dist(self.start_room, center)
                        if dist > max_distance:
                            max_distance = dist
                            self.end_room = center
                print(f"使用空间距离回退方案")
        else:
            # 确保至少有两个有效点
            self.start_room = (self.player.x, self.player.y)
            self.end_room = (self.player.x + 300, self.player.y + 300)

        # 相机初始位置
        self.camera_x = self.player.x - self.screen.get_width() // 2
        self.camera_y = self.player.y - self.screen.get_height() // 2

        print(f"起点: {self.start_room}, 终点: {self.end_room}, 房间数: {len(self.room_centers)}")

    # ------------------- 路径计算相关函数 -------------------

    def _find_farthest_room_by_path(self, start_pos):
        """
        使用BFS找到从起点出发实际路径最远的房间
        返回: (房间中心坐标, 路径距离)
        """
        if not self.room_centers or len(self.room_centers) < 2:
            return None, 0

        # 找到起点所在房间
        start_room = self._find_closest_room_center(start_pos[0], start_pos[1])

        # BFS遍历所有可达房间，记录路径距离
        visited = {start_room: 0}  # 房间中心 -> 路径距离
        queue = deque([(start_room, 0)])

        max_distance = 0
        farthest_room = start_room

        while queue:
            current_room, current_dist = queue.popleft()

            # 遍历所有其他房间，检查是否可达
            for room_center in self.room_centers:
                if room_center not in visited:
                    # 检查两个房间是否连通
                    if self._rooms_connected(current_room, room_center):
                        # 计算实际路径距离（曼哈顿距离作为近似）
                        path_dist = current_dist + self._manhattan_dist(current_room, room_center)
                        visited[room_center] = path_dist
                        queue.append((room_center, path_dist))

                        # 更新最远房间
                        if path_dist > max_distance:
                            max_distance = path_dist
                            farthest_room = room_center

        return farthest_room, max_distance

    def _rooms_connected(self, room1, room2):
        """
        检查两个房间中心是否通过地板连通
        使用简化的BFS检查
        """
        from map import TILE_SIZE

        # 转换为瓦片坐标
        x1, y1 = int(room1[0] // TILE_SIZE), int(room1[1] // TILE_SIZE)
        x2, y2 = int(room2[0] // TILE_SIZE), int(room2[1] // TILE_SIZE)

        # 边界检查
        if not (0 <= x1 < self.map.width and 0 <= y1 < self.map.height):
            return False
        if not (0 <= x2 < self.map.width and 0 <= y2 < self.map.height):
            return False

        # BFS检查连通性
        visited = set()
        queue = deque([(x1, y1)])
        visited.add((x1, y1))

        # 限制搜索范围，提高性能
        max_steps = 1000
        steps = 0

        while queue and steps < max_steps:
            x, y = queue.popleft()
            steps += 1

            if x == x2 and y == y2:
                return True

            # 检查四个方向
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    if 0 <= nx < self.map.width and 0 <= ny < self.map.height:
                        if self.map.tiles[ny][nx] == TILE_EMPTY:
                            visited.add((nx, ny))
                            queue.append((nx, ny))

        return False

    # ------------------- 内部逻辑函数 -------------------

    def _manhattan_dist(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _find_closest_room_center(self, x, y):
        if not self.room_centers:
            return (x, y)
        return min(self.room_centers, key=lambda c: self._manhattan_dist((x, y), c))

    def _handle_player_movement(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # 减少条件判断次数，直接计算移动向量
        if keys[pygame.K_w]:
            dy -= self.move_speed
        if keys[pygame.K_s]:
            dy += self.move_speed
        if keys[pygame.K_a]:
            dx -= self.move_speed
        if keys[pygame.K_d]:
            dx += self.move_speed

        # 优化对角线移动计算（避免浮点数乘法）
        if dx != 0 and dy != 0:
            factor = 0.7071  # 预计算√2/2的值
            dx = int(dx * factor) if dx != 0 else 0
            dy = int(dy * factor) if dy != 0 else 0

        # 合并移动检测逻辑
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        r = self.player.radius

        # 减少碰撞检测次数（合并检测）
        can_move_x = self._can_move(new_x, self.player.y, r)
        can_move_y = self._can_move(self.player.x, new_y, r)

        if can_move_x:
            self.player.x = new_x
        if can_move_y:
            self.player.y = new_y

    def _can_move(self, x, y, radius):
        """优化碰撞检测，减少计算量"""
        # 只检测必要的点（简化为四个方向）
        points = [
            (x - radius, y),  # 左
            (x + radius, y),  # 右
            (x, y - radius),  # 上
            (x, y + radius)  # 下
        ]

        # 提前退出检测
        for px, py in points:
            if not self.map.is_passable(px, py):
                return False
        return True

    def _check_victory(self):
        if self._manhattan_dist((self.player.x, self.player.y), self.end_room) <= 30:
            self.victory = True
            self.state = "victory"

    # ------------------- 更新与绘制 -------------------

    def update(self):
        if self.state == "game" and not self.victory:
            self._handle_player_movement()
            self._check_victory()

        # 优化相机平滑跟随（减少计算量）
        target_x = self.player.x - self.screen.get_width() // 2
        target_y = self.player.y - self.screen.get_height() // 2

        # 使用整数运算代替浮点数
        self.camera_x += int((target_x - self.camera_x) * 0.1)
        self.camera_y += int((target_y - self.camera_y) * 0.1)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.map.render(self.screen, self.camera_x, self.camera_y)

        # 绘制玩家（固定屏幕中心）
        player_screen_x = self.screen.get_width() // 2
        player_screen_y = self.screen.get_height() // 2
        pygame.draw.circle(self.screen, self.player.color,
                           (int(player_screen_x), int(player_screen_y)),
                           self.player.radius)

        # 绘制终点（专属标记）
        end_screen_x = self.end_room[0] - self.camera_x
        end_screen_y = self.end_room[1] - self.camera_y

        # 外圈闪烁光环
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.5 + 0.5
        outer_radius = int(20 + pulse * 8)
        pygame.draw.circle(self.screen, (255, 215, 0),
                           (int(end_screen_x), int(end_screen_y)),
                           outer_radius, 2)

        # 中圈旋转星形标记
        angle = pygame.time.get_ticks() * 0.002
        for i in range(8):
            a = angle + i * math.pi / 4
            x1 = end_screen_x + math.cos(a) * 15
            y1 = end_screen_y + math.sin(a) * 15
            x2 = end_screen_x + math.cos(a) * 8
            y2 = end_screen_y + math.sin(a) * 8
            pygame.draw.line(self.screen, (255, 255, 0),
                             (int(x1), int(y1)), (int(x2), int(y2)), 2)

        # 内圈实心圆
        pygame.draw.circle(self.screen, (255, 215, 0),
                           (int(end_screen_x), int(end_screen_y)), 6, 0)
        pygame.draw.circle(self.screen, (255, 100, 0),
                           (int(end_screen_x), int(end_screen_y)), 3, 0)

        # 提示文字
        hint_text = f"坐标: ({int(self.player.x)}, {int(self.player.y)}) | 距终点: {int(self._manhattan_dist((self.player.x, self.player.y), self.end_room))}"
        hint_surface = self.font.render(hint_text, True, (255, 255, 255))
        self.screen.blit(hint_surface, (10, 10))

        if self.victory:
            victory_text = "🎉 到达最远房间！按R重新开始 🎉"
            victory_surface = self.font.render(victory_text, True, (0, 255, 0))
            rect = victory_surface.get_rect(center=(self.screen.get_width() // 2,
                                                    self.screen.get_height() // 2))
            self.screen.blit(victory_surface, rect)

        pygame.display.flip()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.victory:
                    # 重新生成地牢时增加保护机制
                    try:
                        # 尝试重新初始化
                        self.__init__(self.screen, self.font)
                        # 验证地图是否有效
                        if len(self.map.get_room_centers()) < 2:
                            # 地图无效时再次生成
                            self.__init__(self.screen, self.font)
                    except Exception as e:
                        print(f"地图生成失败，重试: {e}")
                        self.__init__(self.screen, self.font)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()