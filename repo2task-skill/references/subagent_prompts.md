# Subagent Prompts

These prompts are stored for reuse. Prefer loading them directly instead of rewriting them ad hoc during each task-generation run.

## Candidate Judgment Prompt

Use this prompt with the judgment subagent before accepting a PR or issue as a task source.

```text
You are evaluating whether a GitHub PR or issue is a good secondary-development task source.

Repository context:
- Repository purpose: <fill>
- Existing module or feature: <fill>

Candidate:
- Source type: <pr|issue|issue+pr>
- Title: <fill>
- Summary: <fill>
- Changed files: <fill>

Return a concise JSON object with these fields:
{
  "accept": true,
  "built_on_existing_feature": true,
  "clear_problem": true,
  "extra_capability_extension": true,
  "reason": "One short sentence",
  "module_name": "Short module name",
  "problem_statement": "Existing feature A works, but B is missing",
  "capability_extension": "What extra capability is added",
  "reject_if_bugfix_only": false
}

Rules:
- Accept only if the candidate is built on an existing feature or module.
- Accept only if the candidate exposes a clear problem or limitation.
- Accept only if the candidate extends capability, compatibility, integration, configurability, or pluggability.
- Reject bugfix-only, regression-only, typo/docs/test-only, dependency-only, and pure refactor candidates.
```

## Task Rewrite Prompt

Use this prompt with the rewrite subagent after a candidate is accepted.

```text
You are rewriting an accepted PR or issue into a benchmark-style secondary-development task.

Keep the rewritten task anchored to:
- the existing module or feature
- the explicit problem statement
- the added capability or compatibility
- the changed-file neighborhood

Output:
1. a solver-facing problem statement for `instruction.md`
2. a metadata summary for `meta_info.md`

Rules:
- `instruction.md` must contain only the task description itself.
- `meta_info.md` must contain motivation, expected behavior, constraints, file anchors, source summary, and rewrite notes.
- Do not rewrite the task into a bugfix framing.
- Do not invent capabilities outside the original module boundary.
```
