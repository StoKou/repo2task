# Task Schema

## Required `task.toml` fields

```toml
version = "1.0"
repo_url = "https://github.com/owner/repo.git"
repo_commit = "<40-char-commit-hash>"
source_type = "pr"
source_id = "123"
source_url = "https://github.com/owner/repo/pull/123"
source_title = "Fix CLI config parsing"
source_state = "merged"
source_merged_at = "2026-03-24T10:00:00Z"
task_type = "new_feature"
difficulty = "medium"
entry_points = ["path/to/file1", "path/to/file2"]
expected_capability = "Add configurable extension capability"
anchor_files = ["path/to/file1", "path/to/file2"]
anchor_modules = ["cli", "config"]
anchor_behavior = "CLI should accept config overrides without breaking baseline parsing"
anchor_tests = ["tests/test_cli.py"]
anchor_commit = "<source-merge-or-anchor-commit>"
rewrite_agent = "subagent-c"
rewrite_strategy = "bounded-variant-from-pr"
feasibility_score = 0.88
filter_reasons = ["high-specificity", "clear-file-locality", "testable"]

# environment setup references
environment_dockerfile = "environment/Dockerfile"
baseline_command = "python3 -m pytest -q"

# test references
phase1_test = "test/phase1_install_check.py"
phase2_test = "test/phase2_task_check.py"
```

Rules:
- `repo_commit` must be immutable hash; never branch/tag name.
- `entry_points` must point to real repository files.
- `expected_capability` must describe observable behavior.
- `source_*` fields must point to a real PR/issue.
- `anchor_*` fields must keep the task grounded in repository files and behavior.
- `rewrite_*` fields must explain how the accepted candidate was rewritten.

## Required `instruction.md` sections

- task description
- motivation
- expected behavior
- constraints
- affected modules/files
- original PR/issue summary
- what was rewritten
- what stayed anchored
- why task is implementable in this repo
- Step 1-5 analysis summary

## Test Phases

### Phase 1: Installation verification

Must verify:
- fixed commit checkout or equivalent repository import into the image
- Docker environment builds successfully
- baseline runnable state

### Phase 2: Task verification

Must verify:
- expected behavior outcome
- no baseline regression
- deterministic, behavior-driven checks independent of implementation details
