---
name: repo2task
description: Convert a GitHub/local repository into executable benchmark task bundles using Step 1-5 flow: quickstart understanding, capability abstraction, role-based task generation, mandatory modification planning, and reproducible packaging.
---

# Repo2Task Skill

Use this skill when the user wants to parse a repository and produce executable, testable, reproducible secondary-development task packages.

## Core Objective

Transform one repository into multiple isolated task bundles. Each bundle must include:
- clear instruction (`instruction.md`)
- task metadata with fixed commit (`task.toml`)
- containerized environment (`environment/`)
- reference solution (`solution/`)
- automated verification (`test/`)

## Step-by-Step Workflow (Mandatory)

### Step 1: Quickstart Understanding

Extract:
- repository purpose
- target use cases
- input/output patterns
- minimal runnable usage

Mode switching rules:
- Mode A (documentation-driven): `README/docs/examples` first
- Mode B (code-driven fallback): infer from entry points and modules if docs are missing

### Step 2: Capability Abstraction

Build a capability map including:
- core functionalities
- key modules and responsibilities
- interfaces (CLI/API/library)
- existing workflows
- extension points
- replaceable components

### Step 3: Role-based Task Generation

Generate at least 4 tasks from these roles:
- Product Engineer
- Integration Engineer
- Platform Engineer
- QA Engineer

Task constraints:
- grounded in real repository capabilities
- feasible without full rewrite
- explicit entry points and expected capability

### Step 4: Modification Planning (Required)

For each task, explicitly define:
- files to modify
- functions/components to add or change
- expected behavior changes
- minimal-change justification

### Step 5: Task Packaging

Package each task independently as:

```text
task_xxx/
├── instruction.md
├── task.toml
├── environment/
├── solution/
└── test/
```

## Generated File Requirements

### instruction.md
Must include:
- task description
- motivation
- expected behavior
- constraints
- affected modules/files
- Step 1-4 analysis summary

### task.toml
Must include:
- `repo_url`
- `repo_commit` (fixed hash, never branch)
- `role`
- `task_type`
- `difficulty`
- `entry_points`
- `expected_capability`
- environment setup info
- test references

### environment/
Must include:
- `Dockerfile`
- `setup.sh`

Must support:
- repository checkout to fixed commit
- dependency installation
- minimal runnable baseline state

### solution/
Contains reference implementation:
- minimal code changes only
- scripts/patch/files as needed

### test/
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

## References

- `references/workflow.md`
- `references/task-schema.md`
- `assets/instruction_template.md`
- `assets/task_toml_template.toml`
