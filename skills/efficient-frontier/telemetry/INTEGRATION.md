# Integration guide: efficient-frontier

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

- `README.md:18` — - Treats delegated findings as leads that the frontier model verifies before
- `README.md:22` — ## When To Use It
- `README.md:28` — Skip it when the work is tiny, when edits are all in the same fragile files, or
- `README.md:29` — when the next step depends on one immediate blocker you need to inspect yourself.
- `README.md:44` — and spot-check verification before presenting the final answer.
- `README.md:52` — Use `--update-instructions` when you want the orchestration convention added to
- `SKILL.md:23` — 5. Integrate and review centrally before presenting the result.
- `SKILL.md:35` — - A verification command fails twice after a reasonable fix or retry.
- `SKILL.md:43` — verification that matters before claiming completion. If delegated agents
- `SKILL.md:52` — - Coding: delegate bounded patches, refactors, or mechanical edits when file
- `SKILL.md:58` — - Debugging: send independent agents after separate theories, logs, or repro
- `SKILL.md:63` — - Do not delegate the immediate blocker if your next step depends on it.
- `SKILL.md:65` — - Do not trust subagent conclusions blindly when the risk is high; inspect the
- `SKILL.md:67` — - Do not claim universal savings. The pattern works best when exploration and

### Verification candidates

- `README.md:25` — repo exploration, refactors, multi-file implementation, test-failure clustering,
- `README.md:26` — or PR-quality validation.
- `README.md:33` — The frontier model should choose the validation plan. Cheaper agents can run
- `README.md:44` — and spot-check verification before presenting the final answer.
- `SKILL.md:17` — extraction, browser/testing passes, log reduction, test failure clustering,
- `SKILL.md:42` — important cited files, skim high-risk diffs, and rerun or spot-check the
- `SKILL.md:54` — - Testing: let the frontier model choose the validation strategy and scripts,
- `VERIFICATION.md:9` — Delegated-agent orchestration depends on the active Codex host and is not run by this local check.
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given a delegated test failing twice, stop and report command, failure, and residual risk.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
