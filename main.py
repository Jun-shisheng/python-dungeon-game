"""
Python 地牢游戏 - 主程序
支持全屏自适应窗口和开场动画
"""

import pygame
import os
import sys

# 初始化 Pygame
pygame.init()

# 窗口尺寸（窗口模式）
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# 获取屏幕尺寸（用于全屏模式，已注释）
# info = pygame.display.Info()
# SCREEN_WIDTH = info.current_w
# SCREEN_HEIGHT = info.current_h

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)
GOLD = (255, 215, 0)
RED = (200, 0, 0)

# 获取资源路径的辅助函数
def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        # PyInstaller打包后的临时文件夹
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class Game:
    """游戏主类"""
    
    def __init__(self):
        # 创建窗口模式（节省资源）
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("地牢冒险")
        
        # 全屏模式代码（已注释，需要时取消注释）
        # self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        
        # 设置时钟
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 加载资源
        self.load_resources()
        
        # 游戏状态：intro（开场动画）, menu（主菜单）, game（游戏进行中）
        self.state = "intro"
        
        # 开场动画相关
        self.intro_alpha = 0
        self.intro_fade_in = True
        self.intro_timer = 0
        self.intro_duration = 3000  # 开场动画持续3秒
        
        # 标题动画相关
        self.title_y_offset = -100
        self.title_animation_speed = 2
        
    def load_resources(self):
        """加载游戏资源"""
        # 初始化背景
        self.background = None
        try:
            # 尝试加载背景图片
            bg_path = resource_path(os.path.join("images", "background", "bg_intro.png"))
            if os.path.exists(bg_path):
                try:
                    self.background = pygame.image.load(bg_path)
                    self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                except (pygame.error, IOError, OSError) as e:
                    print(f"背景图片加载失败: {e}")
                    self.background = None
        except Exception as e:
            print(f"背景图片路径处理失败: {e}")
            self.background = None
        
        # 初始化字体为默认值，确保不会为None
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 24)
        
        try:
            # 尝试加载自定义字体
            font_path = resource_path(os.path.join("fonts", "press_start_2p.ttf"))
            if os.path.exists(font_path):
                try:
                    self.title_font = pygame.font.Font(font_path, 48)
                    self.subtitle_font = pygame.font.Font(font_path, 24)
                except (pygame.error, IOError, OSError) as e:
                    print(f"加载自定义字体失败: {e}，使用默认字体")
            else:
                # 使用系统字体（支持中文）
                # Windows系统字体
                if sys.platform == "win32":
                    # 尝试使用Windows系统中文字体
                    font_names = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong"]
                    font_loaded = False
                    for font_name in font_names:
                        try:
                            test_font = pygame.font.SysFont(font_name, 48)
                            # 测试是否能渲染中文
                            test_surface = test_font.render("测试", True, (255, 255, 255))
                            if test_surface.get_width() > 0:
                                self.title_font = test_font
                                self.subtitle_font = pygame.font.SysFont(font_name, 24)
                                font_loaded = True
                                break
                        except (pygame.error, Exception):
                            continue
                    if not font_loaded:
                        print("无法加载中文字体，使用默认字体")
                else:
                    # Linux/Mac使用系统字体
                    try:
                        self.title_font = pygame.font.SysFont(None, 48)
                        self.subtitle_font = pygame.font.SysFont(None, 24)
                    except (pygame.error, Exception) as e:
                        print(f"加载系统字体失败: {e}，使用默认字体")
        except Exception as e:
            print(f"字体加载过程出错: {e}，使用默认字体")
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # 空格键或回车键跳过开场动画
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if self.state == "intro":
                        self.state = "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标点击跳过开场动画
                if self.state == "intro":
                    self.state = "menu"
    
    def draw_intro(self):
        """绘制开场动画"""
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # 如果没有背景图片，绘制渐变色背景
            self.screen.fill(DARK_GRAY)
        
        # 标题淡入动画（通过调整颜色亮度实现淡入效果）
        title_text = "地牢冒险"
        # 根据alpha值调整颜色亮度实现淡入效果
        alpha_factor = max(0.0, min(1.0, self.intro_alpha / 255.0))
        fade_gold = tuple(int(c * alpha_factor) for c in GOLD)
        if self.title_font:
            title_surface = self.title_font.render(title_text, True, fade_gold)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 
                                                         WINDOW_HEIGHT // 2 + self.title_y_offset))
            self.screen.blit(title_surface, title_rect)
        
        # 副标题（淡入效果，比标题稍慢）
        subtitle_text = "按空格键或点击鼠标开始游戏"
        subtitle_alpha = max(0, self.intro_alpha - 50)
        subtitle_alpha_factor = max(0.0, min(1.0, subtitle_alpha / 255.0))
        fade_white = tuple(int(c * subtitle_alpha_factor) for c in WHITE)
        if self.subtitle_font:
            subtitle_surface = self.subtitle_font.render(subtitle_text, True, fade_white)
            subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, 
                                                              WINDOW_HEIGHT // 2 + 100))
            self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_menu(self):
        """绘制主菜单（临时）"""
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_GRAY)
        
        if self.title_font:
            title_text = "地牢冒险"
            title_surface = self.title_font.render(title_text, True, GOLD)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
            self.screen.blit(title_surface, title_rect)
        
        if self.subtitle_font:
            menu_text = "主菜单（待实现）"
            menu_surface = self.subtitle_font.render(menu_text, True, WHITE)
            menu_rect = menu_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(menu_surface, menu_rect)
            
            hint_text = "按ESC退出"
            hint_surface = self.subtitle_font.render(hint_text, True, WHITE)
            hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
            self.screen.blit(hint_surface, hint_rect)
    
    def update(self):
        """更新游戏逻辑"""
        if self.state == "intro":
            # 更新开场动画参数
            if self.intro_fade_in:
                self.intro_alpha += 5
                self.title_y_offset += self.title_animation_speed
                if self.intro_alpha >= 255:
                    self.intro_alpha = 255
                    self.intro_fade_in = False
                if self.title_y_offset >= 0:
                    self.title_y_offset = 0
            else:
                # 保持显示一段时间后淡出
                self.intro_timer += self.clock.get_time()
                if self.intro_timer >= self.intro_duration:
                    self.intro_alpha -= 3
                    if self.intro_alpha <= 0:
                        self.state = "menu"
        elif self.state == "menu":
            pass  # 菜单逻辑待实现
    
    def draw(self):
        """绘制游戏画面"""
        if self.state == "intro":
            self.draw_intro()
        elif self.state == "menu":
            self.draw_menu()
        
        pygame.display.flip()
    
    def run(self):
        """游戏主循环"""
        while self.running:
            self.clock.tick(60)  # 60 FPS
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

