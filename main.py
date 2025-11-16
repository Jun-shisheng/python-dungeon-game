"""
Python 地牢游戏 - 主程序
支持全屏自适应窗口和开场动画
"""

import pygame
import os
import sys
from game_engine import GameEngine

# 初始化 Pygame
try:
    pygame.init()
except Exception as e:
    print(f"Pygame初始化失败: {e}")
    sys.exit(1)

# 窗口尺寸（窗口模式）
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

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
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class Game:
    """游戏主类"""

    def __init__(self):
        try:
            # 创建窗口模式（节省资源）
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("地牢冒险")
        except pygame.error as e:
            print(f"创建游戏窗口失败: {e}")
            pygame.quit()
            raise

        # 设置时钟
        self.clock = pygame.time.Clock()
        self.running = True

        # 加载资源
        self.load_resources()

        # 游戏状态：intro（开场动画）, menu（主菜单）, game（游戏进行中）
        self.state = "intro"

        # 游戏引擎实例（在进入游戏状态时初始化）
        self.game_engine = None

        # 开场动画相关
        self.intro_alpha = 0
        self.intro_fade_in = True
        self.intro_timer = 0
        self.intro_duration = 3000  # 开场动画持续3秒

        # 标题动画相关
        self.title_y_offset = -80  # 调整初始偏移，让标题位置更合适
        self.title_animation_speed = 2

        # 黑色渐亮效果相关
        self.fade_from_black_alpha = 255  # 从255（全黑）逐渐减少到0（完全显示）
        self.fade_from_black_speed = 3  # 渐亮速度（每帧减少的alpha值）
        self.fade_from_black_complete = False  # 渐亮效果是否完成

    def load_resources(self):
        """加载游戏资源"""
        # 初始化背景
        self.background = None
        try:
            # 加载背景图片 Background.png
            bg_path = resource_path(os.path.join("images", "background", "Background.png"))
            if os.path.exists(bg_path):
                try:
                    self.background = pygame.image.load(bg_path)
                    self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    print(f"成功加载背景图片: Background.png")
                except (pygame.error, IOError, OSError) as e:
                    print(f"背景图片加载失败: {e}")
                    self.background = None
            else:
                print("背景图片文件不存在: Background.png")
        except Exception as e:
            print(f"背景图片路径处理失败: {e}")
            self.background = None

        # 初始化字体为默认值，确保不会为None
        self.title_font = pygame.font.Font(None, 72)  # 标题字体（战狼体）
        self.subtitle_font = pygame.font.Font(None, 28)  # 副标题字体（公子体）

        try:
            # 分别加载战狼体（标题）和公子体（副标题）
            fonts_dir = resource_path("fonts")
            title_font_loaded = False
            subtitle_font_loaded = False

            if os.path.exists(fonts_dir):
                # 获取fonts文件夹中的所有字体文件
                font_files = []
                for file in os.listdir(fonts_dir):
                    if file.lower().endswith(('.ttf', '.otf')):
                        font_files.append(file)

                # 加载战狼体（标题）- 优先
                zhanlang_fonts = [
                    "PingFangZhanLangTi.ttf", "PingFangZhanLangTi.otf",  # 英文名
                    "平方战狼体.ttf", "平方战狼体.otf"  # 中文名
                ]
                for font_filename in font_files:
                    if font_filename in zhanlang_fonts:
                        font_path = os.path.join(fonts_dir, font_filename)
                        try:
                            self.title_font = pygame.font.Font(font_path, 80)  # 标题字体大小
                            print(f"✓ 成功加载标题字体（战狼体）: {font_filename}")
                            title_font_loaded = True
                            break
                        except (pygame.error, IOError, OSError) as e:
                            print(f"✗ 加载战狼体失败 ({font_filename}): {e}")

                # 加载公子体（副标题）
                gongzi_fonts = [
                    "PingFangGongZiTi.ttf", "PingFangGongZiTi.otf",  # 英文名
                    "平方公子体.ttf", "平方公子体.otf"  # 中文名
                ]
                for font_filename in font_files:
                    if font_filename in gongzi_fonts:
                        font_path = os.path.join(fonts_dir, font_filename)
                        try:
                            self.subtitle_font = pygame.font.Font(font_path, 32)  # 副标题字体大小
                            print(f"✓ 成功加载副标题字体（公子体）: {font_filename}")
                            subtitle_font_loaded = True
                            break
                        except (pygame.error, IOError, OSError) as e:
                            print(f"✗ 加载公子体失败 ({font_filename}): {e}")

            # 如果字体未完全加载，尝试按特定文件名查找
            if not title_font_loaded or not subtitle_font_loaded:
                custom_font_files = [
                    "PingFangGongZiTi.ttf",  # 平方公子体
                    "PingFangZhanLangTi.ttf",  # 平方战狼体
                    "zhan_ku_gao_duan_hei.ttf",  # 站酷高端黑
                    "pang_men_zheng_dao_cu_shu_ti.ttf",  # 庞门正道粗书体
                    "you_she_biao_ti_hei.ttf",  # 优设标题黑
                    "si_yuan_hei_ti.ttf",  # 思源黑体
                    "press_start_2p.ttf",  # Press Start 2P（像素风格）
                ]

                # 补充加载缺失的字体
                if not title_font_loaded:
                    for font_filename in ["PingFangZhanLangTi.ttf", "平方战狼体.ttf"]:
                        if font_filename in custom_font_files:
                            font_path = resource_path(os.path.join("fonts", font_filename))
                            if os.path.exists(font_path):
                                try:
                                    self.title_font = pygame.font.Font(font_path, 80)
                                    title_font_loaded = True
                                    print(f"✓ 补充加载标题字体: {font_filename}")
                                    break
                                except (pygame.error, IOError, OSError):
                                    continue

                if not subtitle_font_loaded:
                    for font_filename in ["PingFangGongZiTi.ttf", "平方公子体.ttf"]:
                        if font_filename in custom_font_files:
                            font_path = resource_path(os.path.join("fonts", font_filename))
                            if os.path.exists(font_path):
                                try:
                                    self.subtitle_font = pygame.font.Font(font_path, 32)
                                    subtitle_font_loaded = True
                                    print(f"✓ 补充加载副标题字体: {font_filename}")
                                    break
                                except (pygame.error, IOError, OSError):
                                    continue

            # 如果未加载到自定义字体，则使用系统字体
            if not title_font_loaded or not subtitle_font_loaded:
                print("ℹ 部分字体未找到，尝试使用系统字体")
                # 使用系统字体（支持中文）
                # Windows系统字体
                if sys.platform == "win32":
                    # 尝试使用Windows系统中文字体
                    font_names = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong"]
                    sys_font_loaded = False
                    for font_name in font_names:
                        try:
                            test_font = pygame.font.SysFont(font_name, 80 if not title_font_loaded else 72)
                            # 测试是否能渲染中文
                            test_surface = test_font.render("测试", True, (255, 255, 255))
                            if test_surface.get_width() > 0:
                                if not title_font_loaded:
                                    self.title_font = pygame.font.SysFont(font_name, 80)
                                if not subtitle_font_loaded:
                                    self.subtitle_font = pygame.font.SysFont(font_name, 32)
                                sys_font_loaded = True
                                break
                        except (pygame.error, Exception):
                            continue
                    if not sys_font_loaded:
                        print("无法加载中文字体，使用默认字体")
                else:
                    # Linux/Mac使用系统字体
                    try:
                        if not title_font_loaded:
                            self.title_font = pygame.font.SysFont(None, 80)
                        if not subtitle_font_loaded:
                            self.subtitle_font = pygame.font.SysFont(None, 32)
                    except (pygame.error, Exception) as e:
                        print(f"加载系统字体失败: {e}，使用默认字体")
        except Exception as e:
            print(f"字体加载过程出错: {e}，使用默认字体")

    def handle_events(self):
        """处理事件，确保游戏状态下事件正常传递"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "game":
                        self.game_engine = None
                        self.state = "menu"
                    else:
                        self.running = False
                    return
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if self.state == "intro":
                        self.state = "menu"
                    elif self.state == "menu":
                        self._start_new_game()
                elif event.key in [pygame.K_1, pygame.K_KP1]:
                    print("键盘按键：1 - 开始新游戏")
                    self._start_new_game()
                elif self.state == "menu":
                    if event.key in [pygame.K_3, pygame.K_KP3, pygame.K_q]:
                        print("键盘按键：3/Q - 退出游戏")
                        self.running = False
                        return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "intro":
                    self.state = "menu"
                elif self.state == "menu":
                    self._handle_menu_click(event.pos)

        # 游戏状态下传递事件（仅保留重启功能）
        if self.state == "game" and self.game_engine:
            self.game_engine.handle_events(events)

    def _handle_menu_click(self, pos):
        """处理菜单点击事件"""
        screen_width, screen_height = self.screen.get_size()
        new_game_y = screen_height // 2
        quit_y = screen_height // 2 + 50

        def is_clicked(y_pos, pos_y):
            return y_pos - 15 <= pos_y <= y_pos + 15

        if (screen_width//2 - 100 <= pos[0] <= screen_width//2 + 100 and
            is_clicked(new_game_y, pos[1])):
            print("鼠标点击：新游戏")
            self._start_new_game()
        elif (screen_width//2 - 100 <= pos[0] <= screen_width//2 + 100 and
              is_clicked(quit_y, pos[1])):
            print("鼠标点击：退出游戏")
            self.running = False

    def _start_new_game(self):
        """开始新游戏"""
        print("新游戏启动")
        self.game_engine = GameEngine(self.screen, self.subtitle_font)
        self.state = "game"

    def update(self):
        """确保游戏状态下持续更新"""
        if self.state == "intro":
            if not self.fade_from_black_complete:
                self.fade_from_black_alpha -= self.fade_from_black_speed
                if self.fade_from_black_alpha <= 0:
                    self.fade_from_black_alpha = 0
                    self.fade_from_black_complete = True
                return
            if self.intro_fade_in:
                self.intro_alpha += 5
                self.title_y_offset += self.title_animation_speed
                if self.intro_alpha >= 255:
                    self.intro_alpha = 255
                    self.intro_fade_in = False
                if self.title_y_offset >= 0:
                    self.title_y_offset = 0
            else:
                self.intro_timer += self.clock.get_time()
                if self.intro_timer >= self.intro_duration:
                    self.intro_alpha -= 3
                    if self.intro_alpha <= 0:
                        self.state = "menu"
        elif self.state == "game":
            if self.game_engine:
                self.game_engine.update()  # 强制每帧更新游戏引擎

    def draw_intro(self):
        """绘制开场动画"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_GRAY)
        if not self.fade_from_black_complete:
            black_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            black_overlay.set_alpha(int(self.fade_from_black_alpha))
            black_overlay.fill(BLACK)
            self.screen.blit(black_overlay, (0, 0))
            return
        title_text = "地牢冒险"
        alpha_factor = max(0.0, min(1.0, self.intro_alpha / 255.0))
        fade_gold = tuple(int(c * alpha_factor) for c in GOLD)
        if self.title_font:
            title_surface = self.title_font.render(title_text, True, fade_gold)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2,
                                                         WINDOW_HEIGHT // 2 - 80 + self.title_y_offset))
            self.screen.blit(title_surface, title_rect)
        subtitle_text = "按空格键或点击鼠标开始游戏"
        subtitle_alpha = max(0, self.intro_alpha - 50)
        subtitle_alpha_factor = max(0.0, min(1.0, subtitle_alpha / 255.0))
        fade_white = tuple(int(c * subtitle_alpha_factor) for c in WHITE)
        if self.subtitle_font:
            subtitle_surface = self.subtitle_font.render(subtitle_text, True, fade_white)
            subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2,
                                                              WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(subtitle_surface, subtitle_rect)

    def draw_menu(self):
        """绘制游戏菜单"""
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
            options = [
                ("1. 开始新游戏", WINDOW_HEIGHT//2),
                ("3. 退出游戏", WINDOW_HEIGHT//2 + 50)
            ]
            for text, y in options:
                surf = self.subtitle_font.render(text, True, WHITE)
                text_rect = surf.get_rect(center=(WINDOW_WIDTH//2, y))
                self.screen.blit(surf, text_rect)
            hint_text = "使用数字键1-3选择，或点击对应选项"
            hint_surface = self.subtitle_font.render(hint_text, True, (200, 200, 200))
            hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
            self.screen.blit(hint_surface, hint_rect)

    def draw(self):
        """绘制游戏画面"""
        if self.state == "intro":
            self.draw_intro()
        elif self.state == "menu":
            self.draw_menu()
        elif self.state == "game":
            if self.game_engine:
                self.game_engine.draw()
        pygame.display.flip()

    def run(self):
        """游戏主循环（确保60FPS稳定运行）"""
        try:
            while self.running:
                self.clock.tick(60)  # 强制60帧，确保移动流畅
                self.handle_events()
                self.update()
                self.draw()
        except KeyboardInterrupt:
            print("\n游戏被用户中断")
        except Exception as e:
            print(f"游戏运行时发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pygame.quit()
            sys.exit(0)


def main():
    """主函数"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"游戏初始化失败: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()