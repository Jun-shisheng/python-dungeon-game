# Python 随机地牢游戏

一个使用 Pygame 开发的2D地牢冒险游戏。

## 功能特性

- ✅ 开场动画模板（淡入淡出效果）
- ✅ 资源文件管理系统
- ✅ 跨平台兼容（Windows、Mac、Linux）
- ✅ 游戏状态管理（开场动画、菜单、游戏中、暂停状态）
- ✅ 帧率显示与控制功能
- ✅ 完整的用户交互系统（键盘、鼠标支持）
- ✅ 怪物系统（基于康德数字生命思路，包含路径预判和加速接近逻辑）
- ✅ 动态地图生成与渲染优化（仅绘制可见区域）
- ✅ 角色动作系统（包含攻击、闪避等多状态动画）
- ✅ 相机平滑跟随功能
- ✅ 游戏主循环优化

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
- **玩家移动**: WASD
- **玩家操作**: J攻击、K闪避

## 项目结构

```
python-dungeon-game/
├── main.py               # 主程序文件
├── map.py                # 地图绘制文件
├── create_background.py  # 背景创建文件
├── game_engine.py        # 游戏引擎文件
├── character.py          # 角色行为文件
├── sprite_loader.py      # 角色资源加载文件
├── monster.py            # 怪物行为文件
├── monster_loader.py     # 怪物加载文件
├── requirements.txt      # Python依赖包
├── .gitignore            # Git忽略文件配置
├── README.md             # 项目说明（本文件）
├── RESOURCES.md          # 资源文件组织说明
├── images/               # 图片资源
│   ├── background/       # 背景图片
│   ├── monster/          # 怪物资源
|   |    └── GifPreviews/ # 四种动图资源
│   ├── sprites/          # 精灵图
|   |    └── A-Saber/     # 剑士资源
│   └── ui/               # UI元素
├── fonts/                # 字体文件
└── sounds/               # 音频文件
    ├── music/            # 背景音乐
    └── sfx/              # 音效
```


## 开发计划

- [ ] 地图天气系统
- [ ] BOSS设计
- [ ] 物品系统
- [ ] 角色升级系统
- [ ] 音效和背景音乐
- [ ] 存档系统

## 技术栈

- Python 3.x
- Pygame 2.5+

## 许可证

本项目仅供学习使用。使用的资源文件请确保遵守其各自的授权条款。

