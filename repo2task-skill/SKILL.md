---
name: repo2task
description: "Convert GitHub repositories into executable benchmark task bundles by mining real PR/issue candidates, selecting up to 3 feasible tasks per repo, rewriting them with subagents, and packaging them reproducibly."
---

# Repo2Task Skill

Use this skill when the user wants to transform one GitHub repository into executable, testable, reproducible secondary-development task bundles grounded in real PRs or issues.

## Core Objective

Generate up to 3 isolated tasks from one source repository. Every task must be runnable independently and include:
- `instruction.md`
- `task.toml`
- `environment/`
- `solution/`
- `test/`

Hard rules:
- task source priority: `merged PR` > `issue with linked merged PR` > `high-quality standalone issue`
- each repository outputs at most `3` accepted tasks
- if fewer than `3` candidates pass quality gates, output fewer tasks
- do not backfill broad generic tasks when no acceptable PR/issue exists
- persist fetched GitHub metadata locally before re-querying remote endpoints

## Mandatory Workflow (Step 1-6)

### Step 1: Quickstart Understanding

Collect and summarize:
- repository purpose
- target use cases
- input/output patterns
- minimal runnable usage

Mode selection:
- Mode A (`documentation-driven`): prioritize `README*`, `docs/`, `examples/`
- Mode B (`code-driven` fallback): infer from entry points/modules when docs are insufficient

### Step 2: GitHub Candidate Mining

Mine candidate tasks from GitHub and cache them locally under:
- `cache/github/<owner>__<repo>/issues.json`
- `cache/github/<owner>__<repo>/prs.json`
- `cache/github/<owner>__<repo>/candidates.json`

Collect for each PR/issue:
- `source_type` (`pr`, `issue`, `issue+pr`)
- `source_id`, `source_url`, `source_title`, `source_state`
- merged/closed timestamps when available
- changed files
- related commits / patch links when available
- linked issue/PR relationships when available

### Step 3: Candidate Filtering And Scoring

Accept candidates only when they satisfy repository-grounded quality gates:
- `specificity`
- `file_locality`
- `testability`
- `reproducibility`
- `scope_fit`
- `independence_from_external_services`

Selection rules:
- choose up to `3` candidates per repository
- prefer merged PRs with clear changed-file anchors
- skip repository entirely if no candidate passes the minimum bar

### Step 4: Subagent Rewrite

Use subagents to rewrite accepted candidates into benchmark tasks:
- subagent A: summarize the source PR/issue and extract anchors
- subagent B: score feasibility and filter weak candidates
- subagent C: rewrite accepted candidates into task instructions in the required bundle format
- main agent: review, normalize, and finalize the rewritten task

Rewrite constraints:
- stay anchored to source changed files / nearby modules
- keep the observable behavior aligned with the original PR/issue intent
- allow bounded variation, but do not drift into unrelated capability invention
- preserve repository implementability at the fixed commit

### Step 5: Modification Planning (Required)

For each accepted task, explicitly define:
- source PR/issue summary
- files to modify
- functions/components to add or change
- expected behavior changes
- minimal-change justification
- why the rewritten task is implementable in this repository

### Step 6: Task Packaging

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
- original PR/issue summary
- what was rewritten
- what stayed anchored to the source
- why the task is implementable in this repo
- Step 1-5 analysis summary

### `task.toml`
Must include:
- `repo_url`
- `repo_commit` (fixed hash, never branch)
- source provenance fields
- `task_type`
- `difficulty`
- `entry_points`
- `expected_capability`
- anchor files/modules/behavior/tests
- rewrite metadata
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
- Reuse cached GitHub metadata before making new issue/PR requests.
- Do not fabricate tasks when the repository lacks high-quality PR/issue candidates.

## References

- `references/workflow.md`
- `references/task-schema.md`
- `assets/instruction_template.md`
- `assets/task_toml_template.toml`
