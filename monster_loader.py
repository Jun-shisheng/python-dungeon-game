import pygame
import os
import sys
import re
import random
import imageio
from collections import defaultdict


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MonsterLoader:
    def __init__(self, monster_dir="images/monster/GifPreviews"):
        self.monster_dir = resource_path(monster_dir)
        self.sprite_frames = defaultdict(dict)
        self.loaded = False
        self.sprite_size = (64, 64)

    # =========================================
    # 清洗怪物类型，保证与 Monster 一致
    # =========================================
    def _clean_type(self, filename):
        name = filename.lower()

        # 去掉 idle/run 以及后缀（兼容ldle拼写错误）
        name = re.sub(r"(idle|ldle|run).*\.gif", "", name)

        # 去掉符号、数字
        name = name.replace("_", "").replace("-", "")
        name = re.sub(r"\d+", "", name).strip()

        # 标准化怪物类型名称（处理特殊情况）
        name = name.replace("draculaldle", "dracula")
        name = name.replace("mummydle", "mummy")
        name = name.replace("tshirtdudeldle", "tshirtdude")
        name = name.replace("zombieldle", "zombie")

        return name

    # =========================================
    # 加载所有 GIF 动画
    # =========================================
    def load_monster_gifs(self):
        if not os.path.exists(self.monster_dir):
            print(f"❌ 怪物目录不存在: {self.monster_dir}")
            return False

        print("\n========== 加载怪物动画 ==========")

        for filename in os.listdir(self.monster_dir):
            if not filename.lower().endswith(".gif"):
                continue

            full = os.path.join(self.monster_dir, filename)
            fname = filename.lower()

            # 动画类型（兼容ldle拼写错误）
            if "idle" in fname or "ldle" in fname:
                anim = "idle"
            elif "run" in fname:
                anim = "run"
            else:
                print(f"⚠️ 无法识别动画类型，跳过: {filename}")
                continue

            monster_type = self._clean_type(fname)

            try:
                frames = self._load_gif_frames(full)
                self.sprite_frames[monster_type][anim] = frames
                print(f"✅ 加载 {monster_type}.{anim} → {len(frames)} 帧")

            except Exception as e:
                print(f"❌ 加载失败：{filename}: {e}")

        self.loaded = True
        return True

    # =========================================
    # GIF 解析（修复Buffer长度错误）
    # =========================================
    def _load_gif_frames(self, gif_path):
        frames = []
        try:
            # 使用更稳定的GIF加载方式
            import imageio.v2 as imageio
            with imageio.get_reader(gif_path, format='GIF') as reader:
                for frame in reader:
                    # 转换为RGBA格式
                    frame_rgba = frame[:, :, :4] if frame.shape[-1] > 4 else frame
                    frame_rgba = frame_rgba.astype('uint8')  # 确保数据类型正确

                    # 转换为Pygame表面
                    surf = pygame.image.frombuffer(
                        frame_rgba.tobytes(),
                        (frame_rgba.shape[1], frame_rgba.shape[0]),
                        "RGBA"
                    ).convert_alpha()
                    surf = pygame.transform.scale(surf, self.sprite_size)
                    frames.append(surf)

        except Exception as e:
            # 增强错误处理
            print(f"❌ GIF加载错误 {gif_path}: {str(e)}")
            # 尝试多种降级方案
            try:
                # 尝试用Pillow加载
                from PIL import Image, ImageSequence
                img = Image.open(gif_path)
                for frame in ImageSequence.Iterator(img):
                    frame = frame.convert('RGBA')
                    mode = frame.mode
                    size = frame.size
                    data = frame.tobytes()
                    surf = pygame.image.fromstring(data, size, mode).convert_alpha()
                    surf = pygame.transform.scale(surf, self.sprite_size)
                    frames.append(surf)
            except Exception as e2:
                print(f"❌ Pillow加载也失败: {str(e2)}")
                # 终极降级：创建带问号的占位图
                placeholder = pygame.Surface(self.sprite_size, pygame.SRCALPHA)
                pygame.draw.rect(placeholder, (100, 100, 100, 200),
                                 (0, 0, self.sprite_size[0], self.sprite_size[1]))
                font = pygame.font.SysFont(None, 24)
                text = font.render("?", True, (255, 255, 0))
                text_rect = text.get_rect(center=placeholder.get_rect().center)
                placeholder.blit(text, text_rect)
                frames.append(placeholder)

        # 确保至少有一帧
        if not frames:
            placeholder = pygame.Surface(self.sprite_size, pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (100, 0, 0, 200),
                             (0, 0, self.sprite_size[0], self.sprite_size[1]))
            frames.append(placeholder)

        return frames

    # =========================================
    # 获取动画（保证至少返回 idle）
    # =========================================
    def get_monster_animation(self, monster_type, anim_type):
        if not self.loaded:
            self.load_monster_gifs()

        m = monster_type.lower()
        a = anim_type.lower()

        # 如果没有加载到任何怪物，创建默认占位动画
        if not self.sprite_frames:
            print("⚠️ 没有加载到任何怪物动画，创建默认占位动画")
            placeholder = pygame.Surface(self.sprite_size, pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (0, 255, 255, 180), (0, 0, self.sprite_size[0], self.sprite_size[1]))
            return [placeholder]

        # 如果不存在该怪物类型 → 自动 fallback 到任意可用怪
        if m not in self.sprite_frames:
            print(f"⚠️ 未找到怪物 {m}，随机替代")
            m = random.choice(list(self.sprite_frames.keys()))

        # 没有该动画 → 强制 idle
        anims = self.sprite_frames[m]
        if a not in anims:
            print(f"⚠️ {m} 缺少 {a} 动画，使用 idle 替代")
            return anims.get("idle", [])

        return anims[a]

    # =========================================
    # 随机返回一个正确的怪物类型（增加空值保护）
    # =========================================
    def get_random_monster_type(self):
        if not self.sprite_frames:
            print("⚠️ 没有可用的怪物类型！")
            return None  # 或创建默认类型
        return random.choice(list(self.sprite_frames.keys()))