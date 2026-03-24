# Workflow Reference

This file defines the canonical repo2task process.

## Step 1: Quickstart Understanding

Preferred sources:
1. `examples/` and `docs/`
2. `README*`
3. entry points from code when docs are missing

Required outputs:
- what the repo does
- use cases
- input/output
- minimal runnable example

## Step 2: Capability Abstraction

Required capability map fields:
- core functionalities
- key modules
- interfaces
- workflows
- extension points
- replaceable components

## Step 3: Role-based Tasks

Minimum roles:
- Product Engineer
- Integration Engineer
- Platform Engineer
- QA Engineer

Each task must include entry points tied to real files.

## Step 4: Modification Planning

Each task must include:
- file list
- function/component changes
- behavior delta
- minimal modification justification

## Step 5: Packaging

Each task directory is isolated and benchmark-ready:
- `instruction.md`
- `task.toml`
- `environment/`
- `solution/`
- `test/`
