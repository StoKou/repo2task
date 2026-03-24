# 🚀 repo2task - 仓库转任务包生成器

[![Language](https://img.shields.io/badge/Language-中文-red?style=flat-square)](#)
[![Platform](https://img.shields.io/badge/Platform-OpenCode%20%7C%20Claude--Code-blue?style=for-the-badge)](#)
[![Output](https://img.shields.io/badge/Output-Benchmark--Style-2ECC71?style=for-the-badge)](#)
[![Focus](https://img.shields.io/badge/Focus-Repo%20Secondary%20Dev-orange?style=for-the-badge)](#)

> ⚡ 一句话，把仓库文档变成可执行的二次开发任务包。

**宣传标语：**
- 从“看文档”到“做任务”，中间不再手工拆需求。
- 不是只给建议，而是直接产出可跑的任务目录。
- 让 AI 不止会解释仓库，更会推进仓库改造。

`repo2task` 会解析仓库的 `examples/docs/README`，自动生成 benchmark 风格任务目录：
- `instruction.md`（问题定义）
- `task.toml`（任务元信息）
- `environment/`（Docker 与配置）
- `solution/`（解题脚本与说明）
- `test/`（校验脚本）

## ⚡ 快速开始

一句话导入 skill：

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" && mkdir -p "$CODEX_HOME/skills" && cp -R ./repo2task-skill "$CODEX_HOME/skills/repo2task"
```

一句话使用 skill 解析 repo：

```text
请使用 repo2task skill，解析这个仓库并生成任务包：https://github.com/junegunn/fzf
```

## 📦 输出结构

```text
<out>/<gitname>/<subtopic>/
├── instruction.md
├── task.toml
├── environment/
├── solution/
└── test/
```

## 📚 相关文档

- [QUICKSTART.md](/mnt/d/2026/skillsfolder/code/repo2task/QUICKSTART.md)
- [EXAMPLES.md](/mnt/d/2026/skillsfolder/code/repo2task/EXAMPLES.md)
- [docs/OUTPUT_SPEC.md](/mnt/d/2026/skillsfolder/code/repo2task/docs/OUTPUT_SPEC.md)
