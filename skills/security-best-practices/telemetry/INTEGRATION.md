# Integration guide: security-best-practices

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
| Before step 1 | `run.started` | `task_category` (requested mode) |
| After step 2 (load matching references) | `verification` (`phase=scope`) | `languages_detected`, `references_loaded_count`, `reference_coverage_complete` |
| After step 4 (choose mode / analyze) | `decision` (`phase=analyze`) | `mode`, `findings_count`, `trust_boundaries_considered` |
| After a written Report mode output | `verification` (`phase=report`) | `findings_by_severity`, `secrets_reported_location_only` |
| Before returning output | `run.finished` | `mode`, `findings_count`, `awaiting_approval` |
| When a maintainer later dismisses or reprioritizes a finding | `user.correction` | `original_severity`, `correction`, `trust_boundary` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`decision`/`verification` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:27-29` — "Trigger only for explicit security requests or secure coding work in supported languages: Python, JavaScript/TypeScript, and Go" — became `languages_detected`.
- `SKILL.md:34-36` — step 2 "Load every matching reference... including both frontend and backend references for a full-stack application" — became `references_loaded_count`/`reference_coverage_complete`.
- `SKILL.md:40-43` — step 4's three requested-mode options — became the `mode`/`task_category` enum.
- `SKILL.md:74-76` — General-cautions trust-boundary list (authentication, authorization, tenant ownership, validation, injection, secrets, logging, cookies, CSRF, CORS, redirects, uploads, dependency reachability) — became the `trust_boundaries_considered` enum.
- `SKILL.md:49-54` — Report mode's severity-grouped findings and "Report secret type and location only; require rotation when exposure is plausible" — became `findings_by_severity`/`secrets_reported_location_only`.
- `SKILL.md:56` — "After reporting, wait for explicit approval before implementing fixes" — became `awaiting_approval`.

### Execution candidates

- None detected statically; this skill has no bundled scripts, only reference documents, to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
