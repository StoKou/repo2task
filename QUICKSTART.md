# Quick Start

## 1) 安装 Skill

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

也可参考：
- `/mnt/d/2026/skillsfolder/code/repo2skill/README_ZH.md` 的手动复制安装方式

## 2) 生成任务包

以 GitHub 仓库为输入：

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo junegunn/fzf \
  --out ./generated
```

以仓库列表 JSON 为输入：

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build-from-json \
  --repos-json /path/to/repos.json \
  --index 0 \
  --out ./generated
```

## 3) 执行某个任务包校验

```bash
cd generated/junegunn-fzf/task_001
bash test/test.sh
```

## 4) 在对话中触发 Skill

```text
请使用 repo2task skill，解析这个仓库并生成可执行任务包：https://github.com/junegunn/fzf
```
