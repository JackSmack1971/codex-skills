# Integration guide: testing-qa

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

- `SKILL.md:3` — description: "Use to choose or run proportionate QA checks across unit, integration, browser, performance, security, or release quality for an existing change. Do not use when the requested workflow is specifically red-green-refactor TDD; use test-driven-development."
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:24` — 2. Run the project's documented test, lint, type-check, security, and build commands when they exist.
- `SKILL.md:27` — 5. Before completion, verify the acceptance criteria, error paths, security boundaries, accessibility basics, and changed documentation.
- `SKILL.md:29` — The related `test-driven-development`, `security-best-practices`, and `pr-review` skills may be invoked when their narrower scope is actually requested. Do not reference unavailable skills or use `@skill` launcher syntax.

### Verification candidates

- `SKILL.md:3` — description: "Use to choose or run proportionate QA checks across unit, integration, browser, performance, security, or release quality for an existing change. Do not use when the requested workflow is specifically red-green-refactor TDD; use test-driven-development."
- `SKILL.md:4` — compatibility: Requires the project's existing test and QA tools; no runner or dependency is assumed.
- `SKILL.md:11` — - **Trigger and exclusion:** Use to choose or run proportionate QA for an existing change; exclude an explicitly required red-green-refactor cycle, routing to test-driven-development.
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:21` — Use this workflow to choose the smallest test strategy that proves the requested behavior. Inspect the repository first, reuse its existing runner, and report unavailable tooling as UNKNOWN instead of installing a framework by default.
- `SKILL.md:23` — 1. Define the risk and test pyramid: focused unit checks first, integration checks for boundaries, and E2E/browser checks only for critical user paths.
- `SKILL.md:24` — 2. Run the project's documented test, lint, type-check, security, and build commands when they exist.
- `SKILL.md:25` — 3. For browser work, use the in-app browser skill or the project's existing automation; do not assume Playwright, Jest, pytest, or coverage thresholds.
- `SKILL.md:27` — 5. Before completion, verify the acceptance criteria, error paths, security boundaries, accessibility basics, and changed documentation.
- `SKILL.md:29` — The related `test-driven-development`, `security-best-practices`, and `pr-review` skills may be invoked when their narrower scope is actually requested. Do not reference unavailable skills or use `@skill` launcher syntax.
- `VERIFICATION.md:4` — - No test framework or coverage threshold was invented.
- `tests/evaluation-cases.md:4` — 2. **Negative:** Given no reproducible target or test evidence, report the gap rather than claiming QA passed.
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given security, performance, or rollback risk, include the relevant specialized check.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
