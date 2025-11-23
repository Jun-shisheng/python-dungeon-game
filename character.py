import pygame


class Player:
    def __init__(self, name="勇者", sprite_loader=None):
        self.name = name
        self.x = 1
        self.y = 1
        self.radius = 10

        # 精灵核心配置
        self.sprite_loader = sprite_loader
        self.animation_state = "idle"
        self.animation_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_fps = 8  # 8FPS
        self.frame_delay = 1000 // self.animation_fps  # 125ms/帧

        # 攻击状态配置
        self.is_attacking = False
        self.current_attack_type = 1  # 1→2→3循环

        # 朝向
        self.direction = "down"

        # 初始化动画帧
        self._update_animation_frames()

    def _update_animation_frames(self):
        """更新动画帧"""
        if not self.sprite_loader:
            self.animation_frames = []
            return

        # 优先级：攻击 > 移动/待机
        if self.is_attacking:
            anim_key = f"attack{self.current_attack_type}"
            frames = self.sprite_loader.get_animation_frames(anim_key)
        else:
            anim_key = "move" if self.animation_state == "move" else "idle"
            frames = self.sprite_loader.get_animation_frames(anim_key)

        # 降级处理
        self.animation_frames = frames if frames else self.sprite_loader.get_animation_frames("move")

    def set_direction(self, dx, dy):
        """设置朝向"""
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

    def set_animation_state(self, is_moving):
        """设置移动/待机状态"""
        if not self.is_attacking:
            new_state = "move" if is_moving else "idle"
            if new_state != self.animation_state:
                self.animation_state = new_state
                self._update_animation_frames()

    def start_attack(self):
        """触发攻击"""
        if self.is_attacking:
            return

        # 开始新的攻击
        self.is_attacking = True
        self.current_frame = 0
        self.animation_timer = 0
        self._update_animation_frames()
        print(f"⚔️  attack{self.current_attack_type} 开始 ({len(self.animation_frames)}帧)")

    def update_animation(self, delta_time):
        """更新动画帧（核心逻辑）"""
        if not self.animation_frames:
            return

        # 累加计时器
        self.animation_timer += delta_time

        # 检查是否到达下一帧时间
        if self.animation_timer >= self.frame_delay:
            self.animation_timer -= self.frame_delay
            self.current_frame += 1

            # 检查动画是否播放完毕
            if self.current_frame >= len(self.animation_frames):
                if self.is_attacking:
                    # 攻击动画完毕，循环到下一个攻击类型
                    self.current_attack_type = self.current_attack_type % 3 + 1
                    # 退出攻击状态
                    self.is_attacking = False
                    self.current_frame = 0
                    # 重新加载当前状态的帧
                    self._update_animation_frames()
                    print(f"✅ 攻击完毕，下次将使用attack{self.current_attack_type}")
                else:
                    # 非攻击动画循环播放
                    self.current_frame = 0

    def draw(self, screen, screen_x, screen_y):
        """绘制角色"""
        if not self.animation_frames:
            # 降级绘制
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), self.radius)
            return

        # 确保帧索引不越界
        draw_frame = min(self.current_frame, len(self.animation_frames) - 1)

        if draw_frame < 0 or draw_frame >= len(self.animation_frames):
            return

        current_sprite = self.animation_frames[draw_frame]

        # 左方向翻转
        if self.direction == "left":
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # 居中绘制
        sprite_rect = current_sprite.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(current_sprite, sprite_rect)