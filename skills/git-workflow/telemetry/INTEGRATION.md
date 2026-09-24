# Integration guide: git-workflow

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Static candidates from the target

These are inspection hints, not runtime facts.

### Decision candidates

- `SKILL.md:4` — compatibility: Requires Git and a filesystem-readable repository when Git actions are requested.
- `SKILL.md:11` — - **Trigger and exclusion:** Use for requested Git inspection, branching, synchronization, staging, merge, rebase, or recovery; exclude commit authoring when no other Git action is needed, routing to git-commit.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:28` — - Before editing, inspect the repository root, `git status --short --branch`,
- `SKILL.md:30` — - Before synchronization, branch changes, deletion, or remote work, inspect
- `SKILL.md:35` — out of scope unless explicitly requested.
- `SKILL.md:37` — modified file before touching it; never overwrite, restore, reset, clean,
- `SKILL.md:43` — - Do not create or switch branches unless required. Verify current changes
- `SKILL.md:45` — - Do not work directly on a protected or default branch when the repository
- `SKILL.md:47` — - Prefer `git fetch` plus explicit comparison when remote freshness matters;
- `SKILL.md:48` — use `git pull --ff-only` only when fast-forward-only synchronization is
- `SKILL.md:50` — - If local and upstream history diverge, report ahead/behind state instead of
- `SKILL.md:59` — - After staging, inspect status, the cached diff stat, the complete cached
- `SKILL.md:69` — security checks before committing when applicable.

### Verification candidates

- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:43` — - Do not create or switch branches unless required. Verify current changes
- `SKILL.md:60` — diff, and `git diff --check`.
- `SKILL.md:63` — - Verify the staged snapshot contains no credentials, local environment files,
- `SKILL.md:68` — - Run the repository's required tests, lint, format, type-check, build, and
- `SKILL.md:88` — Before deleting a branch, verify it is not checked out elsewhere and whether
- `SKILL.md:97` — remote mutation, re-check status, branch, source and destination refs,
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given a destructive cleanup request, verify exact targets and require explicit approval.

### Execution candidates

- `SKILL.md:87` — recoverable checkpoint when practical. For `git clean`, run a dry run first.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
