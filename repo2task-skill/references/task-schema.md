# Task Schema

## Required task.toml fields

```toml
repo_url = "https://github.com/owner/repo"
repo_commit = "<40-char-commit-hash>"
role = "Product Engineer"
task_type = "new_feature"
difficulty = "medium"
entry_points = ["path/to/file1", "path/to/file2"]
expected_capability = "Add configurable extension capability"
```

## Test phases

- Phase 1 installation verification
  - verify fixed commit checkout
  - verify environment setup success
  - verify baseline command passes

- Phase 2 task verification
  - verify expected behavior artifacts/outputs
  - verify no baseline regression
  - verify behavior-based assertions independent of implementation details
