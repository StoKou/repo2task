# Workflow Reference

This document defines the canonical repo2task process. All generated tasks must follow this sequence exactly.

## Step 1: Quickstart Understanding

Goal: establish a minimal, runnable understanding of the repository.

Inputs (priority order):
1. `README*`
2. `docs/`, `examples/`
3. source entry points (fallback)

Mode rules:
- Use `documentation-driven` if docs provide actionable usage.
- Switch to `code-driven` when docs are absent/insufficient.

Required output fields:
- repository purpose
- target use cases
- input/output patterns
- minimal runnable command

## Step 2: Capability Abstraction

Build a capability map with these required fields:
- core functionalities
- key modules and responsibilities
- interfaces (`CLI`, `API`, library)
- existing workflows
- extension points
- replaceable components

## Step 3: Role-based Task Generation

Generate at least 4 tasks and cover all required roles:
- Product Engineer
- Integration Engineer
- Platform Engineer
- QA Engineer

Constraints per task:
- task is anchored to real repository files
- task is feasible with incremental edits
- entry points are explicit
- expected capability is explicit and testable

## Step 4: Modification Planning (Mandatory)

For each task, define:
- files to modify
- functions/components to add or change
- expected behavior delta
- minimal-change justification

## Step 5: Task Packaging

Each task must be isolated and reproducible:

```text
task_xxx/
├── instruction.md
├── task.toml
├── environment/
├── solution/
└── test/
```

Quality bar:
- fixed commit hash only
- deterministic tests
- behavior-based assertions (avoid implementation coupling)
