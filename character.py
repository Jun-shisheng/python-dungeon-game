import pygame


class Player:
    def __init__(self, name="勇者", sprite_loader=None):
        self.name = name
        self.x = 1
        self.y = 1
        self.radius = 10

        # 精灵动画相关初始化
        self.sprite_loader = sprite_loader
        self.animation_state = "idle"  # 初始状态：待机
        self.animation_frames = []  # 当前动画帧列表
        self.current_frame = 0  # 当前帧索引
        self.animation_timer = 0  # 动画计时器
        self.animation_fps = 8  # 动画帧率（可调整）
        self.frame_delay = 1000 // self.animation_fps  # 每帧间隔（毫秒）

        # 动作状态标记
        self.is_attacking = False
        self.is_hurt = False
        self.is_dead = False

        # 角色朝向（down/up/left/right）
        self.direction = "down"
        self._update_animation_frames()

    def _update_animation_frames(self):
        if not self.sprite_loader:
            self.animation_frames = []
            return
        # 优先处理特殊状态
        if self.is_attacking:
            frames = self.sprite_loader.get_animation_frames("attack")
        elif self.is_hurt:
            frames = self.sprite_loader.get_animation_frames("hurt")
        elif self.is_dead:
            frames = self.sprite_loader.get_animation_frames("die")
        else:
            frames = self.sprite_loader.get_animation_frames(self.animation_state)

        # 关键修复：如果没获取到帧，降级为待机动画
        self.animation_frames = frames if frames else self.sprite_loader.get_animation_frames("idle")
        # 确保帧索引不越界
        self.current_frame = min(self.current_frame, len(self.animation_frames) - 1)

    def set_direction(self, dx, dy):
        """根据移动向量设置角色朝向（适配WASD）"""
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

    def set_animation_state(self, is_moving):
        """根据是否移动切换动画状态（移动/待机）"""
        self.animation_state = "move" if is_moving else "idle"
        self._update_animation_frames()

    def attack(self):
        if not self.is_dead:
            self.is_attacking = True
            self.current_frame = 0  # 新增：重置帧索引
            self.animation_timer = 0  # 新增：重置计时器
            self._update_animation_frames()

    def hurt(self):
        if not self.is_dead:
            self.is_hurt = True
            self.current_frame = 0  # 新增：重置帧索引
            self.animation_timer = 0  # 新增：重置计时器
            self._update_animation_frames()

    def die(self):
        """触发死亡动画"""
        self.is_dead = True
        self._update_animation_frames()

    def update_animation(self, delta_time):
        if not self.animation_frames:
            return
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_delay:
            # 关键修复：先判断是否是最后一帧，再处理状态重置
            if self.current_frame == len(self.animation_frames) - 1:
                # 动画播放完毕，重置状态
                if self.is_attacking:
                    self.is_attacking = False
                elif self.is_hurt:
                    self.is_hurt = False
                # 重新获取当前状态的动画帧（避免卡空）
                self._update_animation_frames()
                # 重置帧索引到0（从头播放新动画）
                self.current_frame = 0
            else:
                # 不是最后一帧，正常切换下一帧
                self.current_frame += 1
            self.animation_timer = 0  # 重置计时器

    def draw(self, screen, screen_x, screen_y):
        """绘制角色（精灵动画/红点降级）"""
        if not self.animation_frames:
            # 精灵加载失败时，降级为红点（避免游戏崩溃）
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), self.radius)
            return

        # 获取当前帧，并根据朝向翻转（向左时水平翻转）
        current_sprite = self.animation_frames[self.current_frame]
        if self.direction == "left":
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # 精灵居中绘制（与角色位置对齐）
        sprite_rect = current_sprite.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(current_sprite, sprite_rect)