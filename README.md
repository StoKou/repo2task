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

`repo2task` 会先理解仓库文档与 examples，再优先挖掘 GitHub 上真实的 `PR/issue` 作为任务来源，并将通过筛选的候选重写成 benchmark 风格任务目录：
- `instruction.md`（只保留任务本身）
- `meta_info.md`（动机、预期行为、约束、来源、锚点与分析）
- `task.toml`（任务元信息）
- `environment/`（仅 `Dockerfile`）
- `solution/`（解题脚本与说明）
- `test/`（校验脚本）

当前 skill 的核心约束：
- 优先 `merged PR`，其次 `issue + linked merged PR`，最后才是高质量 standalone issue
- 每个 GitHub 仓库最多生成 `3` 个任务
- 如果没有足够好的候选，就少生成或跳过，不回填宽泛任务
- 使用 subagent 对候选进行摘要、筛选和格式重写
- `environment/` 仅保留 `Dockerfile`，仓库导入和安装逻辑都写入镜像构建流程

## ⚡ 快速开始

### 1) 下载仓库并安装 skill（手动复制）

```bash
git clone https://github.com/StoKou/repo2task
cd repo2task

# OpenCode（推荐）
mkdir -p ~/.config/opencode/skills
cp -R ./repo2task-skill ~/.config/opencode/skills/repo2task

# Claude Code（兼容）
# mkdir -p ~/.claude/skills
# cp -R ./repo2task-skill ~/.claude/skills/repo2task
```

安装方式可参考：
- `/mnt/d/2026/skillsfolder/code/repo2skill/README_ZH.md`（手动复制安装）

### 2) 在对话中使用 skill 解析仓库

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
- `repo2task-skill/references/skillsbench-sanity/hello-world/`（环境与结构参考）
