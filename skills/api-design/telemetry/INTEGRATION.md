# Integration guide: api-design

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
| Before step 1 | `run.started` | `task_category` (transport family) |
| After step 2 (specify transport shape) | `decision` (`phase=contract`) | `transport`, `error_codes_count`, `empty_states_covered` |
| After step 3 (cross-cutting concerns) | `decision` (`phase=concerns`) | `concerns_addressed` |
| After step 4 (naming/compatibility/sensitive-data/observability check) | `verification` (`phase=check`) | `naming_consistent`, `compatibility_risk_found`, `sensitive_data_exposure_found`, `observability_defined` |
| Before returning output | `run.finished` | `transport`, `error_codes_count`, `concerns_addressed_count`, `boundary_additions_avoided` |
| When a reviewer later changes a contract decision | `user.correction` | `original_decision`, `correction`, `concern_category` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11` — trigger/exclusion boundary naming HTTP, RPC, GraphQL, and internal API contracts — became the `task_category`/`transport` enum.
- `SKILL.md:27` — "Specify transport shape, inputs, outputs, validation, empty states, and stable error codes" — became `error_codes_count`/`empty_states_covered`.
- `SKILL.md:29-30` — authentication, authorization, rate limits, pagination/filtering, idempotency, consistency, and timeout expectations — became the `concerns_addressed` enum.
- `SKILL.md:31` — "Check naming, compatibility, sensitive-data exposure, and observability" — became the `check`-phase `verification` fields.
- `SKILL.md:41-43` — Boundary section (no versioning/pagination/abstraction without need; never expose internal errors, secrets, or unauthorized data) — became `boundary_additions_avoided` and `sensitive_data_exposure_found`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
