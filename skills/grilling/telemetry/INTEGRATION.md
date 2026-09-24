# Integration guide: grilling

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

- `SKILL.md:12` — - Walk each design branch in dependency order, resolving decisions before dependent questions.
- `SKILL.md:14` — - Explore the codebase when it can answer the question instead of asking the user.

### Verification candidates

- `SKILL.md:3` — description: "Use for a new interactive plan or design stress-test, asking one recommended question at a time until shared understanding. Do not use for explicit /grill-me compatibility invocations; route those to grill-me."
- `VERIFICATION.md:6` — - Validation: frontmatter name matches the directory; required `name` and `description` are present; no Claude-only fields or paths remain.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
