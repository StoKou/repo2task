# repo2task

`repo2task` 是一个把 GitHub 仓库转成“二次开发任务包”的 Skill 工程。

它会先拉取/读取仓库，再基于 `examples`、`docs`、`README` 生成可执行任务目录：
- 问题说明（`instruction.md`）
- 任务配置（`task.toml`）
- 运行环境（`environment/`）
- 解题方案（`solution/`）
- 校验脚本（`test/`）

## 快速入口

- 5 分钟上手: [QUICKSTART.md](/mnt/d/2026/skillsfolder/code/repo2task/QUICKSTART.md)
- 使用示例: [EXAMPLES.md](/mnt/d/2026/skillsfolder/code/repo2task/EXAMPLES.md)
- 输出规范: [docs/OUTPUT_SPEC.md](/mnt/d/2026/skillsfolder/code/repo2task/docs/OUTPUT_SPEC.md)

## 仓库结构

```text
repo2task/
├── README.md
├── QUICKSTART.md
├── EXAMPLES.md
├── docs/
│   └── OUTPUT_SPEC.md
└── repo2task-skill/
    ├── SKILL.md
    ├── scripts/
    │   └── generate_repo2task.py
    ├── references/
    └── assets/
```

## 安装 Skill 到 CLI

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R ./repo2task-skill "$CODEX_HOME/skills/repo2task"
```

## 一条命令生成任务

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo junegunn/fzf \
  --out ./generated
```

或从 `repos.json` 直接按索引生成：

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build-from-json \
  --repos-json /mnt/d/2026/skillsfolder/code/data/reposkills/repos.json \
  --index 0 \
  --out ./generated
```

## 产物目录（摘要）

```text
<out>/<gitname>/<subtopic>/
├── instruction.md
├── task.toml
├── environment/
├── solution/
└── test/
```

详细字段见 [docs/OUTPUT_SPEC.md](/mnt/d/2026/skillsfolder/code/repo2task/docs/OUTPUT_SPEC.md)。
