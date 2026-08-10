---
name: using-git-worktrees
description: Use to create or verify isolated Git worktree setup when parallel or branch-isolated work is requested. Do not use for the complete GitHub issue-to-PR lifecycle; github-issue-to-pr composes this skill for that case.
compatibility: Requires Git and Python 3.11+; setup commands are detected but never evaluated through a shell string.
---

# Using Git Worktrees

## Minimum contract

- **Trigger and exclusion:** Use when isolated Git worktree setup or verification is requested or genuinely required for parallel branch work; exclude complete issue-to-PR lifecycle, routing to github-issue-to-pr.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Use this skill only when isolation is requested or parallel implementation genuinely needs it. First detect `.worktrees/` or `worktrees/`, then verify ignore status, construct a branch path, create the worktree, optionally run the project's existing setup, and run its existing baseline tests. Stop with structured output on a missing Git repository, branch collision, setup failure, or test failure.

The portable helper exposes the former actions as subcommands:

```text
python scripts/worktree.py detect
python scripts/worktree.py path --location .worktrees --branch feature/name
python scripts/worktree.py create --path <path> --branch feature/name
python scripts/worktree.py setup --path <path>
python scripts/worktree.py test --path <path>
python scripts/worktree.py verify-ignore --dir .worktrees
```

The current workspace is not a Git repository, so this skill must report that fact rather than create metadata or silently fall back to a copy.

