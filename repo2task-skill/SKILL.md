---
name: repo2task
description: "Convert a GitHub/local repository into executable benchmark task bundles using a strict Step 1-5 flow: quickstart understanding, capability abstraction, role-based task generation, mandatory modification planning, and reproducible packaging."
---

# Repo2Task Skill

Use this skill when the user wants to transform one repository into executable, testable, reproducible secondary-development task bundles.

## Core Objective

Generate multiple isolated tasks from one source repository. Every task must be runnable independently and include:
- `instruction.md`
- `task.toml`
- `environment/`
- `solution/`
- `test/`

## Mandatory Workflow (Step 1-5)

### Step 1: Quickstart Understanding

Collect and summarize:
- repository purpose
- target use cases
- input/output patterns
- minimal runnable usage

Mode selection:
- Mode A (`documentation-driven`): prioritize `README*`, `docs/`, `examples/`
- Mode B (`code-driven` fallback): infer from entry points/modules when docs are insufficient

### Step 2: Capability Abstraction

Produce a capability map covering:
- core functionalities
- key modules + responsibilities
- exposed interfaces (`CLI`/`API`/library)
- existing workflows
- extension points
- replaceable components

### Step 3: Role-based Task Generation

Generate at least 4 tasks, one per role:
- Product Engineer
- Integration Engineer
- Platform Engineer
- QA Engineer

Task quality requirements:
- grounded in real repository capabilities
- feasible by incremental change (no full rewrite)
- explicit entry points
- explicit expected capability outcome

### Step 4: Modification Planning (Required)

For each task, explicitly define:
- files to modify
- functions/components to add or change
- expected behavior changes
- minimal-change justification

### Step 5: Task Packaging

Package each task as:

```text
task_xxx/
├── instruction.md
├── task.toml
├── environment/
├── solution/
└── test/
```

## Generated Files: Hard Requirements

### `instruction.md`
Must include:
- task description
- motivation
- expected behavior
- constraints
- affected modules/files
- Step 1-4 analysis summary

### `task.toml`
Must include:
- `repo_url`
- `repo_commit` (fixed hash, never branch)
- `role`
- `task_type`
- `difficulty`
- `entry_points`
- `expected_capability`
- environment setup references
- test references

### `environment/`
Must include:
- `Dockerfile`
- `setup.sh`

`setup.sh` must support:
- checkout to fixed commit
- dependency installation
- minimal runnable baseline state

### `solution/`
Reference implementation must:
- use minimal code changes only
- include files/scripts/patches needed to demonstrate expected capability

### `test/`
Must include:
- Phase 1 installation verification
- Phase 2 task verification
- deterministic behavior checks (no implementation coupling)

## Script Entry

```bash
python3 scripts/generate_repo2task.py build --repo <path|url|owner/repo> --out <output-dir>
```

```bash
python3 scripts/generate_repo2task.py build-from-json --repos-json <repos.json> --index 0 --out <output-dir>
```

## Execution Rules

- Always pin to immutable commit hash in generated `task.toml`.
- Never use branch names as source of truth.
- Keep task bundles isolated from each other.
- Prefer deterministic checks over snapshot-style coupling.
- If repository docs are weak, explicitly declare mode switch to code-driven inference.

## References

- `references/workflow.md`
- `references/task-schema.md`
- `assets/instruction_template.md`
- `assets/task_toml_template.toml`
