# Python 地牢游戏

一个使用 Pygame 开发的2D地牢冒险游戏。

## 功能特性

- ✅ 全屏自适应窗口（自动适配屏幕分辨率）
- ✅ 开场动画模板（淡入淡出效果）
- ✅ 资源文件管理系统
- ✅ 跨平台兼容（Windows、Mac、Linux）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行游戏

```bash
python main.py
```

## 控制说明

- **ESC**: 退出游戏
- **空格键/回车键/鼠标点击**: 跳过开场动画

## 项目结构

```
python-dungeon-game/
├── main.py              # 主程序文件
├── requirements.txt     # Python依赖包
├── .gitignore          # Git忽略文件配置
├── README.md           # 项目说明（本文件）
├── RESOURCES.md        # 资源文件组织说明
├── images/             # 图片资源
│   ├── background/     # 背景图片
│   ├── sprites/        # 精灵图
│   └── ui/             # UI元素
├── fonts/              # 字体文件
└── sounds/             # 音频文件
    ├── music/          # 背景音乐
    └── sfx/            # 音效
```

## 添加资源文件

### 推荐步骤：

1. **下载背景图片**（可选）
   - 从 [Kenney.nl](https://kenney.nl) 或 [OpenGameArt.org](https://opengameart.org) 下载地牢风格背景
   - 保存为 `images/background/Background.png`
   - 程序会自动检测并使用

2. **下载字体**（可选）
   - 推荐使用 [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P)
   - 下载后保存为 `fonts/press_start_2p.ttf`

3. **查看详细说明**
   - 更多资源获取建议请查看 `RESOURCES.md`

## 开发计划

- [ ] 主菜单界面
- [ ] 游戏场景
- [ ] 角色系统
- [ ] 战斗系统
- [ ] 音效和背景音乐
- [ ] 存档系统

## 技术栈

- Python 3.x
- Pygame 2.5+

## 许可证

本项目仅供学习使用。使用的资源文件请确保遵守其各自的授权条款。

