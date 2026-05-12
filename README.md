# Saudi English Game Generator

AI 驱动的 HTML 英语学习小游戏自动生产。终端两键出游戏。

## 快速开始

```bash
pip install openai
python generate.py
```

输入 CEFR 级别 → 回车 → 等 30 秒 → HTML 在 `output/` 目录。

## 13 款游戏

| # | 游戏 | 交互模型 | 类型 |
|---|------|----------|------|
| 1 | 咖啡配对大师 | 点击选项 | 选择题 |
| 2 | 我的利雅得日常 | 点击选项 | 选择题 |
| 3 | 周末时光机 | 拖拽排序 | 选择题 |
| 4 | 沙特美食推荐王 | 点击选项 | 选择题 |
| 5 | Careem救急 | 滑动卡片 | 选择题 |
| 6 | 我的林荫地图 | 点击选项 | 选择题 |
| 7 | 传话给CEO | 点击选项 | 选择题 |
| 8 | 外交式谈判 | 对话三选一 | 选择题 |
| 9 | 修辞竞技场 | 递进关卡 | 选择题 |
| 10 | 单词捕手 | 移动接掉落单词 | 街机 |
| 11 | 记忆翻牌 | 翻牌配对 | 记忆 |
| 12 | 拼词积木 | 拖字母拼单词 | 拼字 |
| 13 | AI 自由发明 | AI 自定 | 任意 |

## 标配特性

- 三屏架构（Splash → Game → Results）
- Web Audio 程序化音效
- 触觉震动反馈
- PWA 可安装到主屏幕
- localStorage 进度存档
- PC / 平板 / 手机三端响应式
- A1 级别自动英阿双语
- 中东内容审核红线内置
- 51Talk Logo 嵌入

## 目录结构

```
game_gen/
├── prompts/         # 7 套 AI System Prompt
├── output/          # 生成的 HTML 文件
├── generate.py      # CLI 入口
├── templates.py     # 游戏类型 + 难度 + 响应式配置
├── validator.py     # 文件校验
└── config.py        # API 配置
```
