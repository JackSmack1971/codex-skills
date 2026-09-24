# Integration guide: integration-engineering

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

- `SKILL.md:9` — Build the smallest provider integration that remains correct when networks,
- `SKILL.md:16` — 2. Define credentials/configuration boundaries and fail early when required
- `SKILL.md:30` — blindly. Stop when credentials, provider policy, or authoritative version

### Verification candidates

- `SKILL.md:20` — 4. For webhooks, verify authenticity, handle duplicates, acknowledge quickly,
- `SKILL.md:22` — 5. Add test-mode coverage, redacted structured logs, useful metrics, and a
- `SKILL.md:24` — 6. Verify success, provider failure, timeout, rate limit, malformed response,
- `tests/evaluation-cases.md:3` — 1. **Normal:** Given an OAuth webhook integration, ground behavior in current provider documentation and verify signatures.
- `tests/evaluation-cases.md:4` — 2. **Negative:** Given untrusted callback data, reject processing without validation, replay protection, and authorization.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
