import pygame
import os
import sys
import re
from collections import defaultdict

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SpriteLoader:
    def __init__(self, sprite_dir="images/sprites/Adventurer-Saber/Individual Sprites"):
        self.sprite_dir = resource_path(sprite_dir)
        self.sprite_frames = defaultdict(list)
        self.loaded = False
        self.sprite_size = (64, 64)

    def load_sprites(self):
        if not os.path.exists(self.sprite_dir):
            print(f"警告：精灵文件夹不存在 - {self.sprite_dir}")
            return False
        # ------------------- 新增：闪避动画配置（仿照攻击） -------------------
        animation_definitions = {
            "idle": r"idle",
            "move": r"run",
            "attack1": r"attack1",
            "attack2": r"attack2",
            "attack3": r"attack3",
            "evade1": r"evade1",  # 适配adventurer-evade1-xx.png
            "evade2": r"evade2",  # 适配adventurer-evade2-xx.png
            "evade3": r"evade3"   # 适配adventurer-evade3-xx.png
        }
        # ---------------------------------------------------------------------
        file_list = os.listdir(self.sprite_dir)
        for filename in file_list:
            if not filename.lower().endswith(".png"):
                continue
            for anim_key, pattern in animation_definitions.items():
                # 匹配规则：包含"adventurer-"且包含对应pattern（如evade1）
                if "adventurer-" in filename.lower() and re.search(pattern, filename.lower()):
                    try:
                        full_path = os.path.join(self.sprite_dir, filename)
                        img = pygame.image.load(full_path).convert_alpha()
                        img = pygame.transform.scale(img, self.sprite_size)
                        self.sprite_frames[anim_key].append((img, filename))
                    except Exception as e:
                        print(f"图像加载失败 {filename}: {e}")
                    break
        # 帧排序（原有代码不变，自动适配闪避帧）
        def extract_frame_number(filename):
            nums = re.findall(r"\d+", filename)
            return int(nums[-1]) if nums else 0
        for anim_key in self.sprite_frames:
            self.sprite_frames[anim_key].sort(key=lambda x: extract_frame_number(x[1]))
            self.sprite_frames[anim_key] = [f[0] for f in self.sprite_frames[anim_key]]
        self.loaded = True
        # 打印加载结果（新增闪避动画信息）
        print("精灵加载完成：")
        for anim_key in animation_definitions:
            print(f"  {anim_key}: {len(self.sprite_frames[anim_key])} 帧")
        return True

    def get_animation_frames(self, anim_type):
        if not self.loaded:
            self.load_sprites()
        frames = self.sprite_frames.get(anim_type, [])
        if not frames:
            print(f"警告：找不到动画 {anim_type}")
        return frames