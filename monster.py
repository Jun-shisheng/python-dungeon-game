import pygame
import math
# 新增：导入 TILE_SIZE 常量
from map import TILE_SIZE


class Monster:
    def __init__(self, monster_type, monster_loader, room, map_instance):
        # 通过 loader 再清洗一次，确保一致
        self.type = monster_type.lower()
        self.loader = monster_loader
        self.map = map_instance
        self.room = room
        # 修正：基于房间中心的像素坐标（与玩家坐标体系一致）
        room_center_x = room["x"] + room["width"] // 2
        room_center_y = room["y"] + room["height"] // 2
        self.x = room_center_x * TILE_SIZE + TILE_SIZE // 2  # 转换为像素坐标
        self.y = room_center_y * TILE_SIZE + TILE_SIZE // 2
        # 动画相关（保持不变）
        self.direction = "right"
        self.animation_state = "idle"
        self.animation_frames = []
        self.current_frame = 0
        self.frame_delay = 6
        self.frame_tick = 0
        self.is_active = False
        # 立刻加载 idle 确保怪物可见
        self._update_animation_frames()



    # ========== 动画切换 ==========
    def _update_animation_frames(self):
        frames = self.loader.get_monster_animation(self.type, self.animation_state)

        if not frames:
            print(f"❌ 严重错误：{self.type}.{self.animation_state} 无帧 → 强制 idle")
            frames = self.loader.get_monster_animation(self.type, "idle")

        self.animation_frames = frames
        self.current_frame = 0

    # ========== 绘制（保证必显示） ==========
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 如果没有帧绝不允许 → idle 补救
        if not self.animation_frames:
            self.animation_state = "idle"
            self._update_animation_frames()

        frame = self.animation_frames[self.current_frame % len(self.animation_frames)]

        if self.direction == "left":
            frame = pygame.transform.flip(frame, True, False)

        rect = frame.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(frame, rect)

    # ========== 激活检测 ==========
    def check_player_in_room(self, player_x, player_y):
        # 计算房间实际像素范围
        room_left = self.room["x"] * TILE_SIZE
        room_right = (self.room["x"] + self.room["width"]) * TILE_SIZE
        room_top = self.room["y"] * TILE_SIZE
        room_bottom = (self.room["y"] + self.room["height"]) * TILE_SIZE

        # 更精确的房间范围检测
        player_in_room = (room_left <= player_x <= room_right and
                          room_top <= player_y <= room_bottom)

        # 激活逻辑
        if player_in_room:
            if not self.is_active:
                self.is_active = True
                self.animation_state = "run"
                self._update_animation_frames()
        else:
            if self.is_active:
                self.is_active = False
                self.animation_state = "idle"
                self._update_animation_frames()
                self._update_animation_frames()

    # ========== 行为更新 ==========
    def update_behavior(self, player_x, player_y):
        if not self.is_active:
            return

        # 计算玩家与怪物的相对位置
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)

        # 参考康德数字生命思路：加入加速接近和路径预判
        if dist > 3:
            # 基础移动速度
            base_speed = 1.0

            # 距离越近速度越快，营造紧迫氛围
            speed_multiplier = 1.0 + min(0.5, (100 - dist) / 200)

            # 预判玩家位置（简单预判）
            predict_factor = 0.1 if dist > 50 else 0
            pred_x = dx * (1 + predict_factor)
            pred_y = dy * (1 + predict_factor)
            pred_dist = math.hypot(pred_x, pred_y)

            # 移动
            self.x += pred_x / pred_dist * base_speed * speed_multiplier
            self.y += pred_y / pred_dist * base_speed * speed_multiplier

        # 更新朝向
        self.direction = "right" if dx >= 0 else "left"

    # ========== 动画更新 ==========
    def update_animation(self):
        if not self.animation_frames:
            return

        self.frame_tick += 1
        if self.frame_tick >= self.frame_delay:
            self.frame_tick = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)