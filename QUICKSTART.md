# Quick Start

## 1) 安装 Skill

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R ./repo2task-skill "$CODEX_HOME/skills/repo2task"
```

## 2) 用脚本生成任务包

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
  --repos-json /mnt/d/2026/skillsfolder/code/data/reposkills/repos.json \
  --index 0 \
  --out ./generated
```

## 3) 进入某个子任务并执行校验

```bash
cd generated/junegunn-fzf/01-vim-neovim-plugin
bash test/test.sh
```

## 4) 在对话中触发 Skill

```text
请使用 repo2task skill，基于 junegunn/fzf 生成 benchmark 风格任务包。
```
