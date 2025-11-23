import pygame
import sys
import random
import math
from collections import deque
from map import Map, TILE_EMPTY, TILE_WALL, TILE_STAIRS
from character import Player
from sprite_loader import SpriteLoader
# 颜色定义（原有代码不变）
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 100, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.state = "game"
        self.victory = False
        self.move_speed = 5
        # 初始化精灵加载器（原有代码不变）
        self.sprite_loader = SpriteLoader()
        print("开始加载精灵资源...")
        self.sprite_loader.load_sprites()
        # 初始化玩家和地图（原有代码不变）
        self.player = Player("勇者", self.sprite_loader)
        self.map = Map(120, 80)
        self.player.x, self.player.y = self.map.player_position
        # ------------------- 新增：给玩家设置地图引用（用于闪避碰撞检测） -------------------
        self.player.set_map_reference(self.map)

        # 获取所有房间中心
        self.room_centers = self.map.get_room_centers()

        # 设置起点和终点
        if len(self.room_centers) >= 2:
            self.start_room = self._find_closest_room_center(self.player.x, self.player.y)

            farthest_room, path_distance = self._find_farthest_room_by_path(
                (self.player.x, self.player.y)
            )

            if farthest_room and farthest_room != self.start_room:
                self.end_room = farthest_room
                print(f"终点设置完成 - 路径距离: {int(path_distance)}")
            else:
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
            self.start_room = (self.player.x, self.player.y)
            self.end_room = (self.player.x + 300, self.player.y + 300)

        # 相机初始位置
        self.camera_x = self.player.x - self.screen.get_width() // 2
        self.camera_y = self.player.y - self.screen.get_height() // 2

        print(f"起点: {self.start_room}, 终点: {self.end_room}, 房间数: {len(self.room_centers)}")

    # ------------------- 路径计算相关函数 -------------------

    def _find_farthest_room_by_path(self, start_pos):
        if not self.room_centers or len(self.room_centers) < 2:
            return None, 0

        start_room = self._find_closest_room_center(start_pos[0], start_pos[1])

        visited = {start_room: 0}
        queue = deque([(start_room, 0)])

        max_distance = 0
        farthest_room = start_room

        while queue:
            current_room, current_dist = queue.popleft()

            for room_center in self.room_centers:
                if room_center not in visited:
                    if self._rooms_connected(current_room, room_center):
                        path_dist = current_dist + self._manhattan_dist(current_room, room_center)
                        visited[room_center] = path_dist
                        queue.append((room_center, path_dist))

                        if path_dist > max_distance:
                            max_distance = path_dist
                            farthest_room = room_center

        return farthest_room, max_distance

    def _rooms_connected(self, room1, room2):
        from map import TILE_SIZE

        x1, y1 = int(room1[0] // TILE_SIZE), int(room1[1] // TILE_SIZE)
        x2, y2 = int(room2[0] // TILE_SIZE), int(room2[1] // TILE_SIZE)

        if not (0 <= x1 < self.map.width and 0 <= y1 < self.map.height):
            return False
        if not (0 <= x2 < self.map.width and 0 <= y2 < self.map.height):
            return False

        visited = set()
        queue = deque([(x1, y1)])
        visited.add((x1, y1))

        max_steps = 1000
        steps = 0

        while queue and steps < max_steps:
            x, y = queue.popleft()
            steps += 1

            if x == x2 and y == y2:
                return True

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
        if self.victory:
            self.player.set_animation_state(is_moving=False)
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w]:
            dy -= self.move_speed
        if keys[pygame.K_s]:
            dy += self.move_speed
        if keys[pygame.K_a]:
            dx -= self.move_speed
        if keys[pygame.K_d]:
            dx += self.move_speed

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx = int(dx * factor) if dx != 0 else 0
            dy = int(dy * factor) if dy != 0 else 0

        new_x = self.player.x + dx
        new_y = self.player.y + dy
        r = self.player.radius

        can_move_x = self._can_move(new_x, self.player.y, r)
        can_move_y = self._can_move(self.player.x, new_y, r)

        if can_move_x:
            self.player.x = new_x
        if can_move_y:
            self.player.y = new_y

        is_moving = dx != 0 or dy != 0
        if is_moving:
            self.player.set_direction(dx, dy)
        self.player.set_animation_state(is_moving)

    def _can_move(self, x, y, radius):
        points = [
            (x - radius, y),
            (x + radius, y),
            (x, y - radius),
            (x, y + radius)
        ]

        for px, py in points:
            if not self.map.is_passable(px, py):
                return False
        return True

    def _check_victory(self):
        if self._manhattan_dist((self.player.x, self.player.y), self.end_room) <= 30:
            self.victory = True
            self.state = "victory"
            print("🎉 到达最远房间！游戏胜利！")

    # ------------------- 更新与绘制 -------------------

    def update(self):
        """游戏更新循环"""
        delta_time = self.clock.tick(self.FPS)


        if self.state == "game" and not self.victory:
            self._handle_player_movement()
            self._check_victory()

        # 始终驱动动画更新（包括胜利状态）
        self.player.update_animation(delta_time)

        # 相机跟随
        target_x = self.player.x - self.screen.get_width() // 2
        target_y = self.player.y - self.screen.get_height() // 2

        self.camera_x += int((target_x - self.camera_x) * 0.1)
        self.camera_y += int((target_y - self.camera_y) * 0.1)

    def draw(self):
        self.screen.fill(BLACK)
        self.map.render(self.screen, self.camera_x, self.camera_y)

        # 绘制玩家
        player_screen_x = self.screen.get_width() // 2
        player_screen_y = self.screen.get_height() // 2
        self.player.draw(self.screen, player_screen_x, player_screen_y)

        # 绘制终点
        end_screen_x = self.end_room[0] - self.camera_x
        end_screen_y = self.end_room[1] - self.camera_y

        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.5 + 0.5
        outer_radius = int(20 + pulse * 8)
        pygame.draw.circle(self.screen, GOLD,
                           (int(end_screen_x), int(end_screen_y)),
                           outer_radius, 2)

        angle = pygame.time.get_ticks() * 0.002
        for i in range(8):
            a = angle + i * math.pi / 4
            x1 = end_screen_x + math.cos(a) * 15
            y1 = end_screen_y + math.sin(a) * 15
            x2 = end_screen_x + math.cos(a) * 8
            y2 = end_screen_y + math.sin(a) * 8
            pygame.draw.line(self.screen, YELLOW,
                             (int(x1), int(y1)), (int(x2), int(y2)), 2)

        pygame.draw.circle(self.screen, GOLD,
                           (int(end_screen_x), int(end_screen_y)), 6, 0)
        pygame.draw.circle(self.screen, ORANGE,
                           (int(end_screen_x), int(end_screen_y)), 3, 0)

        # 提示文字
        hint_text = f"坐标: ({int(self.player.x)}, {int(self.player.y)}) | 距终点: {int(self._manhattan_dist((self.player.x, self.player.y), self.end_room))} | 按J攻击，按K闪避"
        hint_surface = self.font.render(hint_text, True, WHITE)
        self.screen.blit(hint_surface, (10, 10))

        if self.victory:
            victory_text = "🎉 到达最远房间！按R重新开始 🎉"
            victory_surface = self.font.render(victory_text, True, GREEN)
            rect = victory_surface.get_rect(center=(self.screen.get_width() // 2,
                                                    self.screen.get_height() // 2))
            bg_rect = rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect, 0)
            pygame.draw.rect(self.screen, GOLD, bg_rect, 2)
            self.screen.blit(victory_surface, rect)

        pygame.display.flip()

    def handle_events(self, events):
        """处理游戏事件"""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # J键攻击 - 最优先检查
                if event.key == pygame.K_j:
                    if not self.victory:
                        self.player.start_attack()
                    continue

                if event.key == pygame.K_k:
                    if not self.victory:
                        self.player.start_evade()  # 调用闪避方法
                    continue
                # R键重新开始
                if event.key == pygame.K_r and self.victory:
                    try:
                        self.__init__(self.screen, self.font)
                        if len(self.map.get_room_centers()) < 2:
                            self.__init__(self.screen, self.font)
                    except Exception as e:
                        print(f"地图生成失败，重试: {e}")
                        self.__init__(self.screen, self.font)
                    continue

                # ESC键退出
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()