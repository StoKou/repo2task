---
name: repo2task
description: Clone/download a GitHub repository, analyze examples/docs/readme, and generate complex secondary-development tasks where each requirement is a separate subtopic folder with instruction.md and test Python files.
---

# Repo2Task Skill

Use this skill to convert an existing GitHub repo into secondary-development tasks.

## Mandatory Pipeline

1. Resolve source repository:
- Accept local path, GitHub URL, or `owner/repo`.
- If remote, perform shallow clone first (`git clone --depth 1`).

2. Read knowledge sources in this order:
- `examples/` or `example/`
- `docs/` or `doc/`
- root `README*`

3. Build concept-driven requirements:
- Each requirement must begin with concept understanding.
- Requirement content must be non-trivial (compatibility, rollback, observability, risk).

4. Generate output with fixed structure:
- `<out>/<gitname>/<subtopic>/instruction.md`
- `<out>/<gitname>/<subtopic>/test/test1.py`
- `<out>/<gitname>/<subtopic>/test/test2.py`

## Command

```bash
python3 scripts/generate_repo2task.py build --repo <path|url|owner/repo> --out <output-dir>
```

Or from repository list json:

```bash
python3 scripts/generate_repo2task.py build-from-json \
  --repos-json <repos.json> \
  --index 0 \
  --out <output-dir>
```

## Output Quality Rules

- One `subtopic` directory = one requirement.
- `instruction.md` must include:
  - 概念理解
  - 需求说明
  - 实施方案
  - 验收标准
  - 风险与约束
- Each `subtopic` must include test code under `test/`.

## References

- `references/workflow.md`
- `references/task-schema.md`
- `assets/requirement_template.md`
- `assets/task_template.md`
