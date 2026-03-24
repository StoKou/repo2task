# repo2task

`repo2task` 是一个用于 GitHub 仓库二次开发任务生成的 Skill 工程。

它支持先自动 `git clone`（或使用本地仓库），再基于文档理解生成复杂任务包。

## 生成目标

每个需求是一个独立子目录，固定输出结构：

```text
<output>/<gitname>/
├── <subtopic-1>/
│   ├── instruction.md
│   ├── task.toml
│   ├── environment/
│   │   ├── Dockerfile
│   │   ├── skill_config.toml
│   │   └── io_config.json
│   ├── solution/
│   │   ├── solve.sh
│   │   └── solution.md
│   └── test/
│       ├── test.sh
│       └── test_state.py
├── <subtopic-2>/
│   ├── instruction.md
│   ├── task.toml
│   ├── environment/
│   ├── solution/
│   └── test/
└── ...
```

含义：
- `instruction.md`：问题定义与目标约束
- `task.toml`：任务元信息和资源参数
- `environment/`：Docker 与 skill/io 初始配置
- `solution/`：解决命令、代码说明和执行指引
- `test/`：任务校验脚本

## 仓库结构

```text
repo2task/
├── README.md
└── repo2task-skill/
    ├── SKILL.md
    ├── scripts/
    │   └── generate_repo2task.py
    ├── references/
    │   ├── workflow.md
    │   └── task-schema.md
    └── assets/
        ├── requirement_template.md
        └── task_template.md
```

## CLI 快速导入 Skill

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R ./repo2task-skill "$CODEX_HOME/skills/repo2task"
```

## 用法

1) 从单个仓库生成：

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo junegunn/fzf \
  --out ./generated
```

2) 从 `repos.json` 按索引生成（例如第一个项目）：

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build-from-json \
  --repos-json /mnt/d/2026/skillsfolder/code/data/reposkills/repos.json \
  --index 0 \
  --out ./generated
```

## 在对话中使用 Skill

```text
请使用 repo2task skill，对 junegunn/fzf 生成二次开发任务包，并按 gitname/subtopic 输出。
```
