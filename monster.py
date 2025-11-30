import pygame
import math
# 新增：导入 TILE_SIZE 常量
from map import TILE_SIZE
from pygame.math import Vector2

class Projectile:
    """红色小点 projectile 类"""

    def __init__(self, x, y, target_x, target_y, speed=2):
        self.x = x
        self.y = y
        self.radius = 5  # 红色小点大小
        self.color = (255, 0, 0)  # 红色
        self.speed = speed

        # 计算朝向目标的方向向量
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.dx = dx / distance * speed
            self.dy = dy / distance * speed
        else:
            self.dx = 0
            self.dy = 0

    def update(self):
        """更新位置"""
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen, camera_x, camera_y):
        """绘制小点"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)

    def check_collision(self, player):
        """检测是否命中玩家"""
        distance = math.hypot(self.x - player.x, self.y - player.y)
        return distance < self.radius + player.radius


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

        self.max_health = 10  # 怪物最大生命值
        self.current_health = self.max_health  # 当前生命值

        self.type = monster_type.lower()
        self.loader = monster_loader
        self.room = room
        self.map = map_instance

        # 添加远程攻击相关属性
        self.projectiles = []  # 存储发射的小点
        self.attack_cooldown = 1500  # 攻击冷却时间(毫秒)
        self.last_attack_time = 0  # 上次攻击时间
        self.is_ranged = self.type in ["dracula", "mummy"]  # 指定两种远程怪物
        self.attack_range = 200  # 远程攻击范围

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
        # 先绘制小点
        for projectile in self.projectiles:
            projectile.draw(screen, camera_x, camera_y)

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

        # 绘制血条
        health_bar_width = 30
        health_bar_height = 4
        health_ratio = self.current_health / self.max_health

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 血条背景
        pygame.draw.rect(screen, (255, 0, 0),
                         (screen_x - health_bar_width // 2, screen_y - 25,
                          health_bar_width, health_bar_height))
        # 血条前景
        pygame.draw.rect(screen, (0, 255, 0),
                         (screen_x - health_bar_width // 2, screen_y - 25,
                          health_bar_width * health_ratio, health_bar_height))

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
        # 修改 update_behavior 方法，区分近战和远程行为
    def update_behavior(self, player_x, player_y):
        if not self.is_active:
            return

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        self.direction = "right" if dx >= 0 else "left"

        # 远程怪物行为
        if self.is_ranged:
            current_time = pygame.time.get_ticks()
            # 在攻击范围内且冷却结束时发射小点
            if dist < self.attack_range and current_time - self.last_attack_time > self.attack_cooldown:
                self.shoot_projectile(player_x, player_y)
                self.last_attack_time = current_time
            # 远程怪物保持距离
            elif dist < self.attack_range * 0.7:
                self.move_away(dx, dy, dist)
            elif dist > self.attack_range:
                self.move_towards(dx, dy, dist)

        # 近战怪物原有行为
        else:
            if dist > 3:
                base_speed = 1.0
                speed_multiplier = 1.0 + min(0.5, (100 - dist) / 200)
                predict_factor = 0.1 if dist > 50 else 0
                pred_x = dx * (1 + predict_factor)
                pred_y = dy * (1 + predict_factor)
                pred_dist = math.hypot(pred_x, pred_y)
                self.x += pred_x / pred_dist * base_speed * speed_multiplier
                self.y += pred_y / pred_dist * base_speed * speed_multiplier

    # 新增远程攻击方法
    def shoot_projectile(self, target_x, target_y):
        """发射红色小点"""
        self.projectiles.append(Projectile(self.x, self.y, target_x, target_y))

    # 在Monster类中添加通用的房间边界检查方法
    def _clamp_to_room(self, x, y):
        """将坐标限制在房间范围内"""
        room_left = self.room["x"] * TILE_SIZE
        room_right = (self.room["x"] + self.room["width"]) * TILE_SIZE
        room_top = self.room["y"] * TILE_SIZE
        room_bottom = (self.room["y"] + self.room["height"]) * TILE_SIZE

        # 限制坐标在房间范围内
        clamped_x = max(room_left, min(x, room_right))
        clamped_y = max(room_top, min(y, room_bottom))
        return clamped_x, clamped_y

    # 修改move_towards方法，添加边界检查
    def move_towards(self, dx, dy, dist):
        base_speed = 0.8
        new_x = self.x + dx / dist * base_speed
        new_y = self.y + dy / dist * base_speed

        # 应用房间边界限制
        self.x, self.y = self._clamp_to_room(new_x, new_y)

    # 新增辅助方法：远离玩家（添加房间边界限制）
    def move_away(self, dx, dy, dist):
        base_speed = 0.5
        # 计算潜在的新位置
        new_x = self.x - dx / dist * base_speed
        new_y = self.y - dy / dist * base_speed

        # 应用房间边界限制
        self.x, self.y = self._clamp_to_room(new_x, new_y)

        # 计算房间边界（不使用扩展范围，严格限制在房间内）
        room_left = self.room["x"] * TILE_SIZE
        room_right = (self.room["x"] + self.room["width"]) * TILE_SIZE
        room_top = self.room["y"] * TILE_SIZE
        room_bottom = (self.room["y"] + self.room["height"]) * TILE_SIZE

        # 限制新位置在房间范围内
        new_x = max(room_left, min(new_x, room_right))
        new_y = max(room_top, min(new_y, room_bottom))

        # 更新位置
        self.x = new_x
        self.y = new_y

    # 修改 update_animation 方法，添加远程攻击动画支持
    def update_animation(self):
        if not self.animation_frames:
            return

        # 远程攻击时切换动画状态
        current_time = pygame.time.get_ticks()
        if self.is_ranged and current_time - self.last_attack_time < 300:
            if self.animation_state != "attack":
                self.animation_state = "attack"
                self._update_animation_frames()
        else:
            if self.animation_state != "run" and self.is_active:
                self.animation_state = "run"
                self._update_animation_frames()

        # 原有动画更新逻辑
        self.frame_tick += 1
        if self.frame_tick >= self.frame_delay:
            self.frame_tick = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)

    # 添加更新 projectile 的方法
    def update_projectiles(self):
        """更新所有小点位置并移除超出范围的"""
        for projectile in self.projectiles[:]:
            projectile.update()
            # 移除超出房间范围的 projectile
            room = self.room
            room_left = room["x"] * TILE_SIZE - 100
            room_right = (room["x"] + room["width"]) * TILE_SIZE + 100
            room_top = room["y"] * TILE_SIZE - 100
            room_bottom = (room["y"] + room["height"]) * TILE_SIZE + 100

            if not (room_left <= projectile.x <= room_right and
                    room_top <= projectile.y <= room_bottom):
                self.projectiles.remove(projectile)
