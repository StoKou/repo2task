# Output Spec

每个子任务目录必须满足以下结构：

```text
<out>/<repo-slug>/task_xxx/
├── instruction.md
├── meta_info.md
├── task.toml
├── environment/
│   └── Dockerfile
├── solution/
│   ├── solve.sh
│   ├── solution.md
│   └── behavior_contract.json
└── test/
    ├── test.sh
    ├── phase1_install_check.py
    └── phase2_task_check.py
```

## instruction.md

用途：仅定义做题者需要看到的问题本身。

必须包含：
- Task Description
- Expected Behavior
- Constraints

不应包含：
- 动机
- 涉及文件
- 原始 PR/issue 来源说明
- 重写分析过程

## meta_info.md

用途：保存任务来源、动机、文件锚点和分析信息。

必须包含：
- Motivation
- Affected Modules/Files
- Original PR/issue summary
- What was rewritten
- What stayed anchored
- Why task is implementable in this repo
- Step 1-5 Analysis Summary

## task.toml

用途：固定任务元信息和可复现执行锚点。

必须包含：
- `repo_url`
- `repo_commit`（固定 commit hash）
- `source_type`
- `source_id`
- `source_url`
- `source_title`
- `source_state`
- `task_type`
- `difficulty`
- `entry_points`
- `expected_capability`
- `anchor_files`
- `anchor_modules`
- `anchor_behavior`
- `anchor_tests`
- `rewrite_agent`
- `rewrite_strategy`
- `feasibility_score`
- 环境引用：`environment_dockerfile`
- 测试引用：`phase1_test`、`phase2_test`

## environment/

用途：定义可复现环境构建与仓库初始化。

- `Dockerfile`: 基础运行环境，必须负责仓库导入、固定 commit 对齐、依赖安装和 baseline 可运行状态准备

## solution/

用途：提供参考实现（最小改动策略）。

- `solve.sh`: 参考实现执行脚本
- `solution.md`: 变更说明
- `behavior_contract.json`: 行为验收契约

## test/

用途：两阶段自动验证。

- Phase 1（`phase1_install_check.py`）:
  - 验证 setup 成功
  - 验证固定 commit 检出
- Phase 2（`phase2_task_check.py`）:
  - 验证能力行为产出
  - 验证 baseline 无回归
  - 断言基于行为，不耦合实现细节
