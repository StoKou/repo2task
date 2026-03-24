# Task Schema

## Required `task.toml` fields

```toml
version = "1.0"
repo_url = "https://github.com/owner/repo.git"
repo_commit = "<40-char-commit-hash>"
role = "Product Engineer"
task_type = "new_feature"
difficulty = "medium"
entry_points = ["path/to/file1", "path/to/file2"]
expected_capability = "Add configurable extension capability"

# environment setup references
environment_dockerfile = "environment/Dockerfile"
environment_setup = "environment/setup.sh"
baseline_command = "python3 -m pytest -q"

# test references
phase1_test = "test/phase1_install_check.py"
phase2_test = "test/phase2_task_check.py"
```

Rules:
- `repo_commit` must be immutable hash; never branch/tag name.
- `entry_points` must point to real repository files.
- `expected_capability` must describe observable behavior.

## Required `instruction.md` sections

- task description
- motivation
- expected behavior
- constraints
- affected modules/files
- Step 1-4 analysis summary

## Test Phases

### Phase 1: Installation verification

Must verify:
- fixed commit checkout
- environment setup command success
- baseline runnable state

### Phase 2: Task verification

Must verify:
- expected behavior outcome
- no baseline regression
- deterministic, behavior-driven checks independent of implementation details
