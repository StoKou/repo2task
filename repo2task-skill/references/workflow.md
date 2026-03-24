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

## Step 2: GitHub Candidate Mining

Mine and cache GitHub task candidates.

Accepted source priority:
1. `merged PR`
2. `issue with linked merged PR`
3. `standalone high-quality issue`

Cache layout:
- `cache/github/<owner>__<repo>/issues.json`
- `cache/github/<owner>__<repo>/prs.json`
- `cache/github/<owner>__<repo>/candidates.json`

Required mined fields:
- source ids, titles, URLs, states, timestamps
- changed files
- linked issue/PR relationships
- merge or close metadata
- candidate summary and raw source snippet references

## Step 3: Candidate Filtering And Scoring

Evaluate each candidate using these gates:
- specificity
- file locality
- testability
- reproducibility
- scope fit
- independence from external services

Selection rules:
- keep at most `3` accepted tasks per repository
- prefer candidates with clear file and behavior anchors
- if no candidate passes the minimum score, skip task generation for this repository

## Step 4: Subagent Rewrite

Rewrite accepted candidates with subagents:
- subagent A extracts repository and source anchors
- subagent B scores feasibility and filters
- subagent C rewrites accepted candidates into benchmark-style task instructions
- main agent verifies the rewritten output stays repo-grounded

Rewrite outputs must retain:
- source provenance
- changed-file anchors
- observable behavior target
- implementation feasibility at fixed commit

## Step 5: Modification Planning (Mandatory)

For each task, define:
- source PR/issue summary
- files to modify
- functions/components to add or change
- expected behavior delta
- minimal-change justification
- why the task remains implementable in this repository

## Step 6: Task Packaging

Each task must be isolated and reproducible:

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

Quality bar:
- fixed commit hash only
- deterministic tests
- behavior-based assertions (avoid implementation coupling)
- no synthetic fallback tasks when mined candidates are weak
- all repository import/setup/install logic must be encoded in `environment/Dockerfile`
- do not depend on `environment/setup.sh`
