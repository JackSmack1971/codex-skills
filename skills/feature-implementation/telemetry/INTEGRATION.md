# Integration guide: feature-implementation

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

- `SKILL.md:3` — description: "Implement a requested concrete feature in an existing repository as the smallest verified change with focused verification; use narrower cross-layer, TDD, or QA skills when explicit."
- `SKILL.md:11` — - **Trigger and exclusion:** Use after requirements are concrete for an ordinary product change; exclude cross-layer slice planning, explicit TDD, and QA-only requests, routing to vertical-slice, test-driven-development, or testing-qa.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:32` — lint/type checks, and the relevant broader check if available.
- `SKILL.md:38` — dependencies without need. Stop and ask when requirements conflict or a safe
- `SKILL.md:41` — Use `vertical-slice` when the request centers on one user action crossing UI,
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given a trust boundary or data-loss risk, retain validation and recovery even when simplifying.

### Verification candidates

- `SKILL.md:11` — - **Trigger and exclusion:** Use after requirements are concrete for an ordinary product change; exclude cross-layer slice planning, explicit TDD, and QA-only requests, routing to vertical-slice, test-driven-development, or testing-qa.
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:29` — 4. Implement behavior with input validation, error handling, and accessibility
- `SKILL.md:32` — lint/type checks, and the relevant broader check if available.
- `SKILL.md:42` — service/API, persistence, and verification. Use `test-driven-development` for
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given a trust boundary or data-loss risk, retain validation and recovery even when simplifying.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
