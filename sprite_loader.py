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
        self._loading = False

    def load_sprites(self):
        if self.loaded or self._loading:
            return self.loaded
        self._loading = True

        if not os.path.exists(self.sprite_dir):
            print(f"❌ 精灵文件夹不存在 - {self.sprite_dir}")
            self.loaded = True
            self._loading = False
            return False

        # 包含所有动画类型（含idle）
        animation_map = {
            "move": [],
            "idle": [],
            "attack1": [],
            "attack2": [],
            "attack3": [],
        }

        try:
            file_list = [f for f in os.listdir(self.sprite_dir) if f.lower().endswith(".png")]
            print(f"✅ 找到 {len(file_list)} 个PNG文件")

            for filename in file_list:
                if "adventurer-" not in filename:
                    continue
                anim_type = None

                # 严格匹配资源文件名（和你的图片命名完全一致）
                if "adventurer-run-" in filename:
                    anim_type = "move"
                elif "adventurer-idle-" in filename:
                    anim_type = "idle"
                elif "adventurer-attack1-" in filename:
                    anim_type = "attack1"
                elif "adventurer-attack2-" in filename:
                    anim_type = "attack2"
                elif "adventurer-attack3-" in filename:
                    anim_type = "attack3"

                if anim_type:
                    try:
                        sprite_path = os.path.join(self.sprite_dir, filename)
                        sprite = pygame.image.load(sprite_path).convert_alpha()
                        sprite = pygame.transform.scale(sprite, self.sprite_size)

                        # 提取帧编号排序（兼容你的文件命名：-00.png、-01.png等）
                        match = re.search(r'-(\d+)\.png$', filename)
                        frame_num = int(match.group(1)) if match else 999
                        animation_map[anim_type].append((sprite, frame_num, filename))
                        print(f"📥 加载成功：{anim_type} -> {filename}")
                    except Exception as e:
                        print(f"❌ 加载失败 {filename}: {e}")

            # 按帧编号排序并存储
            for anim_type in animation_map:
                sprites_with_nums = animation_map[anim_type]
                sprites_with_nums.sort(key=lambda x: x[1])
                self.sprite_frames[anim_type] = [sprite for sprite, _, _ in sprites_with_nums]

            self.loaded = True
            print("\n📊 精灵加载完成汇总:")
            for anim_type in ["move", "idle", "attack1", "attack2", "attack3"]:
                count = len(self.sprite_frames.get(anim_type, []))
                print(f"  {anim_type}: {count} 帧")

            self._loading = False
            return True
        except Exception as e:
            print(f"❌ 精灵加载异常: {e}")
            self.loaded = True
            self._loading = False
            return False

    def get_animation_frames(self, anim_type):
        if not self.loaded and not self._loading:
            self.load_sprites()
        frames = self.sprite_frames.get(anim_type, [])
        if not frames:
            print(f"⚠️  警告: 动画 '{anim_type}' 找不到任何帧")
        return frames