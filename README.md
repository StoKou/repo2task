# repo2task

`repo2task` 是一个用于 **GitHub 仓库二次开发任务生成** 的 Skill 工程。

它会优先读取目标仓库中的 `example(s)`、`docs`、`README`，自动生成：
- 需求文档（`requirements.md`）
- 任务清单（`tasks.md`）
- 每个任务对应的 `pytest` 测试文件（`tests/test_txxx.py`）

支持三类二次开发场景：
- 新增功能
- 依赖替换（掉包）
- 功能聚合

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

## 在 CLI 中快速导入 Skill

> 以下示例基于 Codex CLI 的本地技能目录约定：`$CODEX_HOME/skills`。

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R ./repo2task-skill "$CODEX_HOME/skills/repo2task"
```

导入后，可在对话中直接使用：

```text
请使用 repo2task skill，基于 <repo-path-or-url> 生成二次开发需求和任务。
```

## 直接用脚本生成任务

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo <本地仓库路径或GitHub URL> \
  --out ./output
```

生成结果：

```text
output/
├── requirements.md
├── tasks.md
└── tests/
    ├── test_t001.py
    ├── test_t002.py
    └── ...
```

## 示例

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo ../repo2skill \
  --out ./demo-output
```

然后在目标工程内实现任务，并运行：

```bash
pytest
```
