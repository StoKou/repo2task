---
name: repo2task
description: Analyze a GitHub repository's examples/docs and generate secondary-development requirement docs, implementation tasks, and per-task pytest scaffolds for feature extension, dependency swapping, and feature aggregation.
---

# Repo2Task Skill

Use this skill when the user wants to transform an existing GitHub repository into actionable secondary-development work items.

## Goal

Produce a practical task package from an existing repository:

1. Read `examples/` or `docs/` first; fallback to root `README*`.
2. Generate requirement docs for secondary development.
3. Convert each requirement into an implementation task.
4. Generate one test file per task.

## Supported Secondary-Development Modes

- New feature extension: add capabilities around existing modules.
- Dependency swap (`掉包`): replace internal/third-party components while preserving external behavior.
- Feature aggregation: combine multiple existing capabilities into one workflow/API.

## Workflow

1. Collect source context:
- Prefer `examples/`, `example/`, `docs/`.
- Include root `README.md` if available.

2. Generate artifacts with script:
- Run:
```bash
python3 scripts/generate_repo2task.py build --repo <repo-path-or-url> --out <output-dir>
```
- Default output files:
  - `requirements.md`
  - `tasks.md`
  - `tests/test_txxx.py`

3. Review and refine:
- Ensure each requirement is scoped to secondary development, not greenfield rewrite.
- Ensure each task has acceptance criteria and test intent.

## Output Rules

- Keep requirements and tasks in Markdown (`.md`).
- Each task must map to at least one generated test file.
- Prefer concrete module-level statements (API endpoint, class, CLI command, workflow).

## References

- Process details: `references/workflow.md`
- Task schema: `references/task-schema.md`
- Requirement template: `assets/requirement_template.md`
- Task template: `assets/task_template.md`
