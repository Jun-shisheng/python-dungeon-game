import pygame
class Player:
    def __init__(self, name="勇者", sprite_loader=None):
        self.name = name
        self.x = 1
        self.y = 1
        self.radius = 10
        # 精灵核心配置（原有代码不变）
        self.sprite_loader = sprite_loader
        self.animation_state = "idle"
        self.animation_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_fps = 8  # 8FPS（与攻击动画一致）
        self.frame_delay = 1000 // self.animation_fps  # 125ms/帧
        # 攻击状态配置（原有代码不变）
        self.is_attacking = False
        self.current_attack_type = 1  # 1→2→3循环
        # ------------------- 新增：闪避状态配置 -------------------
        self.is_evading = False  # 闪避状态标记
        self.current_evade_type = 1  # 闪避类型循环（1→2→3）
        self.evade_distance = 20  # 闪避位移距离（可调整）
        self.evade_completed = False  # 闪避位移是否完成
        # ---------------------------------------------------------
        # 朝向（原有代码不变）
        self.direction = "down"

        self.max_health = 10  # 最大生命值
        self.current_health = self.max_health  # 当前生命值
        # 初始化动画帧（原有代码不变）
        self._update_animation_frames()

    def _update_animation_frames(self):
        """更新动画帧（新增闪避动画优先级）"""
        if not self.sprite_loader:
            self.animation_frames = []
            return
        # 优先级：闪避 > 攻击 > 移动/待机（新增闪避优先级）
        if self.is_evading:
            anim_key = f"evade{self.current_evade_type}"
            frames = self.sprite_loader.get_animation_frames(anim_key)
        elif self.is_attacking:
            anim_key = f"attack{self.current_attack_type}"
            frames = self.sprite_loader.get_animation_frames(anim_key)
        else:
            anim_key = "move" if self.animation_state == "move" else "idle"
            frames = self.sprite_loader.get_animation_frames(anim_key)
        # 降级处理（原有代码不变）
        self.animation_frames = frames if frames else self.sprite_loader.get_animation_frames("move")

    def set_direction(self, dx, dy):
        """设置朝向（原有代码不变）"""
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

    def set_animation_state(self, is_moving):
        """设置移动/待机状态（新增闪避状态判断）"""
        if not self.is_attacking and not self.is_evading:  # 闪避时不切换状态
            new_state = "move" if is_moving else "idle"
            if new_state != self.animation_state:
                self.animation_state = new_state
                self._update_animation_frames()

    def start_attack(self):
        """触发攻击（原有代码不变，不修改）"""
        if self.is_attacking or self.is_evading:  # 新增：闪避时禁止攻击
            return
        self.is_attacking = True
        self.current_frame = 0
        self.animation_timer = 0
        self._update_animation_frames()
        print(f"⚔️  attack{self.current_attack_type} 开始 ({len(self.animation_frames)}帧)")

    # ------------------- 新增：闪避触发方法 -------------------
    def start_evade(self):
        """触发闪避（仿照start_attack逻辑）"""
        if self.is_evading or self.is_attacking:  # 闪避/攻击时禁止重复触发
            return
        # 开始新的闪避
        self.is_evading = True
        self.evade_completed = False  # 重置位移状态
        self.current_frame = 0
        self.animation_timer = 0
        self._update_animation_frames()
        print(f"⚡ evade{self.current_evade_type} 开始 ({len(self.animation_frames)}帧)")
        # 触发闪避位移（根据当前朝向）
        self._do_evade_movement()

    # ------------------- 新增：闪避位移逻辑 -------------------
    def _do_evade_movement(self):
        """根据朝向执行闪避位移（与移动逻辑兼容）"""
        if self.evade_completed:
            return
        # 根据当前朝向计算位移方向
        dx, dy = 0, 0
        if self.direction == "up":
            dy = -self.evade_distance
        elif self.direction == "down":
            dy = self.evade_distance
        elif self.direction == "left":
            dx = -self.evade_distance
        elif self.direction == "right":
            dx = self.evade_distance
        # 计算新位置（与移动碰撞检测逻辑一致）
        new_x = self.x + dx
        new_y = self.y + dy
        r = self.radius
        # 检查位移是否可通行（复用移动的碰撞检测）
        if self._can_evade_move(new_x, self.y, r):
            self.x = new_x
        if self._can_evade_move(self.x, new_y, r):
            self.y = new_y
        # 标记位移完成
        self.evade_completed = True

    # ------------------- 新增：闪避位移碰撞检测 -------------------
    def _can_evade_move(self, x, y, radius):
        """闪避位移的碰撞检测（复用移动的检测逻辑）"""
        points = [
            (x - radius, y),
            (x + radius, y),
            (x, y - radius),
            (x, y + radius)
        ]
        for px, py in points:
            # 复用地图的is_passable方法（需确保Map类实例可访问）
            if hasattr(self, 'map') and not self.map.is_passable(px, py):
                return False
        return True

    def update_animation(self, delta_time):
        """更新动画帧（新增闪避动画逻辑）"""
        if not self.animation_frames:
            return
        # 累加计时器（原有代码不变）
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_delay:
            self.animation_timer -= self.frame_delay
            self.current_frame += 1
            # 检查动画是否播放完毕
            if self.current_frame >= len(self.animation_frames):
                # 新增：闪避动画完毕处理
                if self.is_evading:
                    # 切换到下一个闪避类型（1→2→3循环，仿照攻击）
                    self.current_evade_type = self.current_evade_type % 3 + 1
                    # 退出闪避状态
                    self.is_evading = False
                    self.current_frame = 0
                    # 重新加载当前状态的帧
                    self._update_animation_frames()
                    print(f"✅ 闪避完毕，下次将使用evade{self.current_evade_type}")
                # 原有：攻击动画完毕处理
                elif self.is_attacking:
                    self.current_attack_type = self.current_attack_type % 3 + 1
                    self.is_attacking = False
                    self.current_frame = 0
                    self._update_animation_frames()
                    print(f"✅ 攻击完毕，下次将使用attack{self.current_attack_type}")
                # 原有：非攻击动画循环
                else:
                    self.current_frame = 0

    def draw(self, screen, screen_x, screen_y):
        """绘制角色（原有代码不变，自动适配闪避动画帧）"""
        if not self.animation_frames:
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), self.radius)
            return
        draw_frame = min(self.current_frame, len(self.animation_frames) - 1)
        if draw_frame < 0 or draw_frame >= len(self.animation_frames):
            return
        current_sprite = self.animation_frames[draw_frame]
        # 左方向翻转（原有代码不变）
        if self.direction == "left":
            current_sprite = pygame.transform.flip(current_sprite, True, False)
        sprite_rect = current_sprite.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(current_sprite, sprite_rect)

        # 绘制血条
        health_bar_width = 40
        health_bar_height = 5
        health_ratio = self.current_health / self.max_health

        # 血条背景
        pygame.draw.rect(screen, (255, 0, 0),
                         (screen_x - health_bar_width // 2, screen_y - 30,
                          health_bar_width, health_bar_height))
        # 血条前景
        pygame.draw.rect(screen, (0, 255, 0),
                         (screen_x - health_bar_width // 2, screen_y - 30,
                          health_bar_width * health_ratio, health_bar_height))

    # ------------------- 新增：关联地图碰撞检测（关键） -------------------
    def set_map_reference(self, map_instance):
        """设置地图引用，用于闪避位移的碰撞检测（需在GameEngine中调用）"""
        self.map = map_instance