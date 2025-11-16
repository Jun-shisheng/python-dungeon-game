import pygame
import sys
import random
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

        # 修改 game_engine.py 中的 __init__ 方法中终点选择部分
        # 替换原有房间中心处理逻辑
        self.room_centers = self.map.get_room_centers()
        if len(self.room_centers) >= 2:
            self.start_room = self._find_closest_room_center(self.player.x, self.player.y)
            # 计算每个房间与起点的距离，选择最远的作为终点
            max_distance = -1
            self.end_room = self.start_room
            for center in self.room_centers:
                if center != self.start_room:
                    dist = self._manhattan_dist(self.start_room, center)
                    if dist > max_distance:
                        max_distance = dist
                        self.end_room = center
        else:
            # 确保至少有两个有效点
            self.start_room = (self.player.x, self.player.y)
            self.end_room = (self.player.x + 300, self.player.y + 300)

        # 相机初始位置
        self.camera_x = self.player.x - self.screen.get_width() // 2
        self.camera_y = self.player.y - self.screen.get_height() // 2

        print(f"起点: {self.start_room}, 终点: {self.end_room}, 房间数: {len(self.room_centers)}")

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
        if keys[pygame.K_w]:
            dy -= self.move_speed
        if keys[pygame.K_s]:
            dy += self.move_speed
        if keys[pygame.K_a]:
            dx -= self.move_speed
        if keys[pygame.K_d]:
            dx += self.move_speed

        # 对角线归一化
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # 尝试移动
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        r = self.player.radius

        # 修复碰撞逻辑：分别检测 X 和 Y 方向
        if self._can_move(new_x, self.player.y, r):
            self.player.x = new_x
        if self._can_move(self.player.x, new_y, r):
            self.player.y = new_y

    def _can_move(self, x, y, radius):
        """检查玩家在 (x, y) 是否能移动"""
        # 检测四个点是否可通过
        points = [
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius)
        ]
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

            # 平滑相机跟随玩家
            target_x = self.player.x - self.screen.get_width() // 2
            target_y = self.player.y - self.screen.get_height() // 2
            self.camera_x += (target_x - self.camera_x) * 0.1
            self.camera_y += (target_y - self.camera_y) * 0.1

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.map.render(self.screen, self.camera_x, self.camera_y)

        # 绘制玩家（固定屏幕中心）
        player_screen_x = self.screen.get_width() // 2
        player_screen_y = self.screen.get_height() // 2
        pygame.draw.circle(self.screen, self.player.color,
                           (int(player_screen_x), int(player_screen_y)), self.player.radius)

        # 绘制终点
        end_screen_x = self.end_room[0] - self.camera_x
        end_screen_y = self.end_room[1] - self.camera_y
        pygame.draw.circle(self.screen, (255, 255, 0), (int(end_screen_x), int(end_screen_y)), 12, 3)
        pygame.draw.circle(self.screen, (255, 255, 0), (int(end_screen_x), int(end_screen_y)), 4, 0)

        # 提示文字
        hint_text = f"坐标: ({int(self.player.x)}, {int(self.player.y)}) | 距终点: {int(self._manhattan_dist((self.player.x, self.player.y), self.end_room))}"
        hint_surface = self.font.render(hint_text, True, (255, 255, 255))
        self.screen.blit(hint_surface, (10, 10))

        if self.victory:
            victory_text = "🎉 到达最远房间！按R重新开始 🎉"
            victory_surface = self.font.render(victory_text, True, (0, 255, 0))
            rect = victory_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(victory_surface, rect)

        pygame.display.flip()

    # 修改 game_engine.py 中的 handle_events 方法
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
