import pygame
import os
import sys
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

        animation_types = {
            "idle": "adventurer-idle",  # 待机动画
            "move": "adventurer-run",  # 移动动画
            "attack": "adventurer-attack",  # 攻击动画
            "hurt": "adventurer-hurt",  # 受伤/闪避
            "die": "adventurer-die"  # 死亡动画
        }

        for filename in os.listdir(self.sprite_dir):
            if filename.lower().endswith(".png"):
                for anim_type, prefix in animation_types.items():
                    if filename.startswith(prefix):
                        sprite_path = os.path.join(self.sprite_dir, filename)
                        sprite = pygame.image.load(sprite_path).convert_alpha()
                        sprite = pygame.transform.scale(sprite, self.sprite_size)
                        self.sprite_frames[anim_type].append(sprite)
                        break

        for anim_type in self.sprite_frames:
            self.sprite_frames[anim_type].sort(key=lambda f: int(filename.split("-")[-1].split(".")[0]))

        self.loaded = True
        print(f"成功加载精灵：{list(self.sprite_frames.keys())}")
        return True

    def get_animation_frames(self, anim_type):
        if not self.loaded:
            self.load_sprites()
        return self.sprite_frames.get(anim_type, [])