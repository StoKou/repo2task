# Output Spec

每个子任务目录必须满足以下结构：

```text
<out>/<gitname>/<subtopic>/
├── instruction.md
├── task.toml
├── environment/
│   ├── Dockerfile
│   ├── skill_config.toml
│   └── io_config.json
├── solution/
│   ├── solve.sh
│   └── solution.md
└── test/
    ├── test.sh
    └── test_state.py
```

## instruction.md

用途：描述具体问题与开发边界。

最少包含：
- 问题
- 背景
- 目标
- 开发要求
- 验收标准
- 风险与约束

## task.toml

用途：定义任务元信息与执行资源。

核心段：
- `[metadata]`
- `[verifier]`
- `[agent]`
- `[environment]`

## environment/

用途：定义运行环境与输入输出约束。

- `Dockerfile`: 任务容器基础环境
- `skill_config.toml`: skill 名称、repo、subtopic、开发模式
- `io_config.json`: 输入/输出预期

## solution/

用途：提供解题入口与说明。

- `solve.sh`: 执行脚本（可替换为真实实现命令）
- `solution.md`: 方案步骤与变更范围说明

## test/

用途：自动校验任务包完整性。

- `test.sh`: 统一测试入口
- `test_state.py`: 结构与关键字段断言
