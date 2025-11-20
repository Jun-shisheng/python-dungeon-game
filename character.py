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
        self.animation_fps = 10  # 提高帧率到10FPS，播放更流畅
        self.frame_delay = 1000 // self.animation_fps  # 100ms/帧（适配6帧动画）

        # 攻击状态配置
        self.is_attacking = False
        self.current_attack_type = 1  # 1→2→3循环
        self.attack_frame_index = 0  # 独立的攻击帧索引（避免冲突）
        self.attack_timer = 0

        # 朝向
        self.direction = "down"

        # 初始化动画帧
        self._update_animation_frames()

    def _update_animation_frames(self):
        """更新动画帧（确保攻击帧正确赋值）"""
        if not self.sprite_loader:
            self.animation_frames = []
            return

        # 优先级：攻击动画 > 移动/待机
        if self.is_attacking:
            anim_key = f"attack{self.current_attack_type}"
            frames = self.sprite_loader.get_animation_frames(anim_key)
            # 攻击帧重置为0，避免从中间开始播放
            self.attack_frame_index = 0
        else:
            anim_key = "move" if self.animation_state == "move" else "idle"
            frames = self.sprite_loader.get_animation_frames(anim_key)

        # 降级处理：避免无帧崩溃
        self.animation_frames = frames if frames else self.sprite_loader.get_animation_frames("move")
        self.current_frame = 0

    def set_direction(self, dx, dy):
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

    def set_animation_state(self, is_moving):
        if not self.is_attacking:
            self.animation_state = "move" if is_moving else "idle"
            self._update_animation_frames()

    def start_attack(self):
        """触发攻击（仅非攻击状态可触发）"""
        if not self.is_attacking:
            self.is_attacking = True
            # 切换攻击类型（1→2→3→1）
            self.current_attack_type = self.current_attack_type % 3 + 1
            # 立即更新攻击帧
            self._update_animation_frames()
            print(f"⚔️  触发攻击: attack{self.current_attack_type}（{len(self.animation_frames)}帧）")

    def update_animation(self, delta_time):
        """动画帧自动更新（核心修复：独立控制攻击帧）"""
        if not self.animation_frames:
            return

        # 攻击动画逻辑（独立帧索引+计时器）
        if self.is_attacking:
            self.attack_timer += delta_time
            # 按帧率切换攻击帧（和非攻击动画保持一致节奏）
            if self.attack_timer >= self.frame_delay:
                self.attack_frame_index += 1
                self.attack_timer = 0
                print(f"🔄 攻击帧更新: {self.attack_frame_index}/{len(self.animation_frames)-1}")

                # 攻击动画播放完毕
                if self.attack_frame_index >= len(self.animation_frames):
                    self.is_attacking = False
                    self.attack_frame_index = 0
                    self._update_animation_frames()
                    print(f"✅ 攻击结束，回归{self.animation_state}状态")
                else:
                    self.current_frame = self.attack_frame_index
            return

        # 非攻击动画逻辑（移动/待机循环）
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.animation_timer = 0

    def draw(self, screen, screen_x, screen_y):
        """绘制角色（确保攻击帧正确渲染）"""
        if not self.animation_frames:
            # 降级绘制：红色圆点
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), self.radius)
            return

        # 确保帧索引不越界
        if self.is_attacking:
            draw_frame = self.attack_frame_index
        else:
            draw_frame = self.current_frame
        draw_frame = min(draw_frame, len(self.animation_frames) - 1)
        current_sprite = self.animation_frames[draw_frame]

        # 左方向翻转精灵
        if self.direction == "left":
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # 居中绘制（适配精灵大小）
        sprite_rect = current_sprite.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(current_sprite, sprite_rect)