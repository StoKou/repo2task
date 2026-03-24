---
name: repo2task
description: "Convert GitHub repositories into executable benchmark task bundles by mining PR or issue candidates, keeping only high-quality secondary-development tasks, rewriting them with subagents, and packaging them reproducibly."
---

# Repo2Task Skill

Use this skill when the user wants to transform one GitHub repository into executable, testable, reproducible secondary-development task bundles grounded in real PRs or issues.

## Core Objective

Generate up to 2 isolated tasks from one source repository. Every task must be runnable independently and include:
- `instruction.md`
- `meta_info.md`
- `task.toml`
- `environment/`
- `solution/`
- `test/`

Hard rules:
- task source priority: `merged PR` > `issue with linked merged PR` > `high-quality standalone issue`
- each repository outputs at most `2` accepted tasks
- if fewer than `2` candidates pass the secondary-development bar, output fewer tasks
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

### Step 3: Candidate Filtering

Accept candidates only when they satisfy all of these secondary-development rules:
- they are built on top of an existing repository feature or module
- they expose a clear product or engineering problem worth solving
- they extend the existing feature with extra capability, compatibility, integration, or configurability

Selection rules:
- choose up to `2` candidates per repository
- reject PRs that are mainly bugfixes, regressions, typo/docs/test-only changes, dependency bumps, or pure refactors
- prefer merged PRs whose changed files stay near one existing module and show capability expansion rather than repair
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
- keep the rewritten task framed as secondary development on an existing feature, not as a bugfix
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
├── meta_info.md
├── task.toml
├── environment/
│   └── Dockerfile
├── solution/
└── test/
```

## Generated Files: Hard Requirements

### `instruction.md`
Must include:
- task description

`instruction.md` should only contain the problem statement itself. Do not place expected behavior, constraints, source provenance, motivation, file anchors, or workflow analysis in this file.

### `meta_info.md`
Must include:
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

`Dockerfile` must support:
- repository import or checkout to the fixed commit
- dependency installation
- minimal runnable baseline state
- any setup previously done by shell scripts must be expressed through Docker build steps or the container command/entrypoint
- do not rely on a separate `setup.sh`

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
- Prefer the `skillsbench` task shape where `environment/` contains only a `Dockerfile`.

## Reference Benchmark

For concrete packaging expectations, refer to:
- `references/skillsbench-sanity/hello-world/`

This reference shows the preferred environment shape:
- `environment/` contains only `Dockerfile`
- task execution and verification are separated from environment construction
- task metadata and tests follow a benchmark-style layout

## References

- `references/workflow.md`
- `references/task-schema.md`
- `assets/instruction_template.md`
- `assets/meta_info_template.md`
- `assets/task_toml_template.toml`
