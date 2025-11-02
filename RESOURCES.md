# 资源文件组织说明

## 文件夹结构

```
python-dungeon-game/
├── images/
│   ├── background/       # 背景图片
│   │   └── Background.png  # 开场背景
│   ├── sprites/          # 精灵图（角色、怪物等）
│   └── ui/               # UI元素（按钮、图标等）
├── fonts/
│   └── press_start_2p.ttf  # 像素风格字体（示例）
└── sounds/
    ├── music/            # 背景音乐
    └── sfx/              # 音效
```

## 资源文件规范

### 图片格式
- 推荐使用 **PNG** 格式（支持透明通道）
- 背景图片可以是 JPG 或 PNG
- 命名规范：使用小写字母和下划线，例如：
  - `Background.png`（开场背景）
  - `player_idle.png`（玩家待机动画）
  - `button_start.png`（开始按钮）

### 字体格式
- 推荐使用 **TTF** 或 **OTF** 格式
- 个性字体推荐（免费可商用）：
  - **站酷高端黑** - 简洁现代，适合标题（强烈推荐）
  - **庞门正道粗书体** - 粗犷有力
  - **优设标题黑** - 现代感强
  - **思源黑体** - Adobe/Google开源，清晰易读
  - **平方系列** - 平方公子体、平方战狼体等
  - **清松手写体** - 手写风格
  - **Press Start 2P** - 像素风格（Google Fonts）
- 详细字体使用指南请查看 `FONTS_GUIDE.md`

### 音频格式
- 背景音乐：**OGG** 或 **MP3**
- 音效：**OGG**（推荐，文件更小）或 **WAV**
- 命名规范：使用小写字母和下划线

## 免费可商用素材推荐

### 背景素材（地牢/冒险风格）

1. **Kenney.nl**
   - 网址：https://kenney.nl
   - 提供大量免费游戏素材包
   - 授权：CC0（完全免费商用）

2. **OpenGameArt.org**
   - 网址：https://opengameart.org
   - 搜索标签：background, pixel art, dungeon
   - 注意查看每个素材的授权条款

3. **CraftPix.net**
   - 网址：https://craftpix.net
   - 有免费资源区，搜索 "Free 2D Top-Down Pixel Dungeon Asset Pack"
   - 注意查看授权

4. **itch.io**
   - 网址：https://itch.io/game-assets/free
   - 大量免费和付费游戏素材
   - 注意查看每个资源的授权

### UI 按钮/图标素材

1. **itch.io - Buttons**
   - 搜索 "pixel ui buttons"
   - 很多免费的像素风格UI包

2. **OpenGameArt - Pixel UI pack**
   - 搜索 "Pixel UI pack - 750 assets"
   - 包含按钮、面板、光标等UI元素

3. **CraftPix - Free Buttons**
   - 搜索 "Free Buttons 2D Game Objects"

### 字体素材（像素风格）

1. **Google Fonts**
   - Press Start 2P：https://fonts.google.com/specimen/Press+Start+2P
   - 完全免费商用

2. **dafont.com**
   - 搜索 "pixel font free commercial use"
   - 注意查看每个字体的授权

3. **1001 Fonts**
   - 搜索像素风格字体
   - 查看授权条款

## 使用注意事项

1. **授权检查**：下载素材前务必查看授权条款，确保可以商用
2. **推荐授权类型**：
   - CC0（公共领域，完全免费）
   - MIT License
   - 明确标注 "Free for commercial use"
3. **文件大小**：如果单个文件超过 100MB，考虑使用 Git LFS 或外部存储
4. **路径访问**：代码中使用 `resource_path()` 函数确保跨平台兼容

## 示例资源下载

### 快速开始示例

如果你需要快速测试，可以：

1. 下载一个简单的像素背景（从 Kenney.nl 或 OpenGameArt）
2. 保存为 `images/background/Background.png`
3. 下载 Press Start 2P 字体，保存为 `fonts/press_start_2p.ttf`

程序会自动检测这些资源，如果不存在则使用默认样式。

