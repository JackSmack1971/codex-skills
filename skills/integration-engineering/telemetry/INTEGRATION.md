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

## Wired instrumentation

`SKILL.md`'s `## Telemetry` section wires the following semantic events into
this skill's actual Workflow steps (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (integration type) |
| After step 2 (credentials/configuration boundaries) | `decision` (`phase=configure`) | `credentials_source`, `fails_fast_on_missing_config`, `sandbox_mode_used` |
| After steps 3-4 (implement minimal flow; webhook verification/duplicates) | `decision` (`phase=implement`) | `timeout_set`, `retry_strategy`, `idempotency_handled`, `webhook_signature_verified`, `duplicate_handling` |
| After step 6 (verify success/failure/timeout/rate-limit/malformed/repeated-delivery) | `verification` (`phase=verify`) | `scenarios_verified` |
| Before returning output | `run.finished` | `integration_type`, `retry_strategy`, `scenarios_verified_count`, `test_mode_coverage_added`, `metrics_added`, `runbook_added` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description: "...external APIs, SDKs, webhooks, OAuth, and service providers." — became the `task_category` enum.
- `SKILL.md:16` — step 2 "Define credentials/configuration boundaries and fail early when required configuration is absent" — became `credentials_source`, `fails_fast_on_missing_config`.
- `SKILL.md:14` — step 1 "identify supported API/SDK versions, sandbox mode, limits" — became `sandbox_mode_used`.
- `SKILL.md:18-19` — step 3 "timeouts, safe error mapping, retry rules, and idempotency appropriate to the operation" — became `timeout_set`, `retry_strategy`, `idempotency_handled`.
- `SKILL.md:20-21` — step 4 "verify authenticity, handle duplicates, acknowledge quickly" — became `webhook_signature_verified`, `duplicate_handling`.
- `SKILL.md:22-23` — step 5 "test-mode coverage, redacted structured logs, useful metrics, and a failure/recovery runbook" — became `test_mode_coverage_added`, `metrics_added`, `runbook_added`.
- `SKILL.md:24-25` — step 6 "Verify success, provider failure, timeout, rate limit, malformed response, and repeated-delivery behavior" — became the `scenarios_verified` enum.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
