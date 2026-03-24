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

## Step 3: Candidate Filtering

Evaluate each candidate using these secondary-development rules:
- the PR or issue must build on an existing repository feature or module
- it must surface a clear problem or limitation in that existing feature
- it must solve that problem by extending capability, compatibility, integration, configurability, or pluggability

Selection rules:
- keep at most `2` accepted tasks per repository
- reject bugfix-only, regression-only, docs/test-only, dependency-only, or pure refactor candidates
- prefer candidates with clear file anchors inside one existing module and with evidence of capability expansion
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
