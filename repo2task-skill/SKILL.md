---
name: repo2task
description: Clone/download a GitHub repository, analyze examples/docs/readme, and generate benchmark-style secondary-development tasks. Each requirement becomes one subtopic folder with instruction.md, task.toml, environment/, solution/, and test/.
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
- `<out>/<gitname>/<subtopic>/instruction.md` (问题说明)
- `<out>/<gitname>/<subtopic>/task.toml` (任务元信息)
- `<out>/<gitname>/<subtopic>/environment/` (Docker + skill/io 配置)
- `<out>/<gitname>/<subtopic>/solution/` (解决脚本与说明)
- `<out>/<gitname>/<subtopic>/test/` (校验脚本)

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
- `instruction.md` must describe a concrete problem and constraints.
- `task.toml` must include metadata/verifier/agent/environment sections.
- `environment/` must include `Dockerfile`, `skill_config.toml`, `io_config.json`.
- `solution/` must include executable commands and written notes.
- `test/` must include runnable verification scripts.

## References

- `references/workflow.md`
- `references/task-schema.md`
- `assets/requirement_template.md`
- `assets/task_template.md`
