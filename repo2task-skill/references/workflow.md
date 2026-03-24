# Workflow Reference

## Primary Scan Order

1. `examples/` or `example/`
2. `docs/` or `doc/`
3. root `README*`

This order biases toward runnable usage patterns before narrative docs.

## Requirement Quality Bar

Each requirement should:
- be a secondary-development task (not full rewrite)
- specify one mode: new feature / dependency swap / aggregation
- define acceptance criteria that can be tested

## Task Quality Bar

Each task should:
- map to exactly one primary requirement
- include module boundary and integration impact
- define at least one happy path + one error path test
