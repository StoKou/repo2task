# Output Spec

每个子任务目录必须满足以下结构：

```text
<out>/<repo-slug>/task_xxx/
├── instruction.md
├── task.toml
├── environment/
│   ├── Dockerfile
│   └── setup.sh
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

用途：定义任务目标、约束和 Step 1-4 分析链路。

必须包含：
- Task Description
- Motivation
- Expected Behavior
- Constraints
- Affected Modules/Files
- Step 1-4 Analysis Summary

## task.toml

用途：固定任务元信息和可复现执行锚点。

必须包含：
- `repo_url`
- `repo_commit`（固定 commit hash）
- `role`
- `task_type`
- `difficulty`
- `entry_points`
- `expected_capability`
- 环境引用：`environment_dockerfile`、`environment_setup`
- 测试引用：`phase1_test`、`phase2_test`

## environment/

用途：定义可复现环境构建与仓库初始化。

- `Dockerfile`: 基础运行环境
- `setup.sh`: 拉取仓库并切换到固定 commit，安装依赖并建立 baseline 可运行状态

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
