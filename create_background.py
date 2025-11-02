"""
创建一个简单的地牢风格背景图片
"""

from PIL import Image, ImageDraw
import os

def create_dungeon_background(width=1024, height=768, output_path="images/background/Background.png"):
    """创建简单的地牢背景"""
    # 创建图像
    img = Image.new('RGB', (width, height), color=(40, 35, 35))
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的砖块纹理
    brick_color1 = (60, 55, 50)
    brick_color2 = (30, 25, 20)
    brick_size = 64
    
    for y in range(0, height, brick_size):
        for x in range(0, width, brick_size):
            # 交替颜色创建砖块效果
            color = brick_color1 if (x // brick_size + y // brick_size) % 2 == 0 else brick_color2
            draw.rectangle([x, y, x + brick_size, y + brick_size], fill=color, outline=(20, 15, 10))
    
    # 添加一些装饰性的暗影效果（底部渐变）
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for i in range(height):
        alpha = int((i / height) * 30)  # 底部稍微暗一点
        overlay_draw.rectangle([0, i, width, i + 1], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # 保存图片
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"背景图片已创建: {output_path}")

if __name__ == "__main__":
    create_dungeon_background()

