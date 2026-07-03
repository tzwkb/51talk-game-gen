# Saudi English Game Generator

English | [中文](README_ZH.md)


## Overview

 AI-powered 51Talk English-learning game generator for producing deliverable HTML mini-games quickly.

## Key Capabilities

- Generates mini-game content around 51Talk lesson themes.
- Outputs browser-runnable HTML games.
- Designed for fast production and delivery rather than as a general game engine.

## Usage

 Prepare lesson input and API configuration as described below, then run the repository scripts or CLI workflow.

## Status

 This repository is maintained or used according to the current README notes.

## Notes

 The original notes below keep the exact commands, file names, and generation workflow.

## Command and Configuration Reference

The following code blocks keep commands, paths, filenames, and configuration keys literal; explanatory comments are translated for the English README.

```bash
pip install openai
python generate.py
```

```
game_gen/
├── prompts/         # 7 套 AI System Prompt
├── output/          # 生成的 HTML 文件
├── generate.py      # CLI 入口
├── templates.py     # 游戏类型 + 难度 + 响应式配置
├── validator.py     # 文件校验
└── config.py        # API 配置
```

## Detailed Technical Notes

The primary README keeps the original technical details, history notes, full commands, and file layout. This file maintains the English version of the core documentation; consult the primary README code blocks and paths when exact commands are needed.
