# Integration guide: improve

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
this skill's actual Required-workflow steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (Invocation mode) |
| After step 1 (establish scope) / Invocation parsing | `decision` (`phase=scope`) | `effort`, `focus`, `branch_scoped` |
| After step 4 (reopen and reject candidates) | `verification` (`phase=vet`) | `candidates_considered`, `candidates_rejected`, `rejection_reasons` |
| After step 8 (validate plans, scan sensitive output) | `verification` (`phase=validate`) | `plan_validation_exit_code`, `sensitive_output_flagged`, `retry_count`; preceding `retry` event if repaired |
| Before returning output | `run.finished` | `focus`, `effort`, `findings_count`, `plans_written` |
| When a maintainer or executing agent later disputes the work | `user.correction` | `correction`, `detail` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the effort/focus/rejection-reason aggregation an improvement agent
should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:33-38` — Invocation section (`effort`, `focus`, `branch`, `next`/`features`/`roadmap`, `plan <request>`, `review-plan <path>`) — became `task_category`, `effort`, `focus`, `branch_scoped`.
- `SKILL.md:50-51` — Required workflow step 4: "Independently reopen every cited location. Reject stale, duplicate, generic, unreachable, or intentionally documented candidates." — became `candidates_considered`, `candidates_rejected`, and the `rejection_reasons` enum.
- `SKILL.md:67-72` — Required workflow step 8: `validate_plan.py` / `scan_sensitive_output.py` — became `plan_validation_exit_code`, `sensitive_output_flagged`.
- `SKILL.md:74-79` — Stop conditions — became the `--outcome failure`/`--failure-class` guidance on `finish`.
- `SKILL.md:61-63` — Step 6 (present vetted findings; plan top 3-5 after dependency adjustment) — became `findings_count`/`plans_written` on `finish`.
- `SKILL.md:26` — "If the user requests execution or external publication, stop and ask for a separate explicitly authorized implementation workflow." — informed the `user.correction` block, since this skill's plan is handed to a separate executing agent that can report back infeasibility.

### Execution candidates

- `scripts/rank_findings.py`, `scripts/validate_plan.py`, and `scripts/scan_sensitive_output.py` remain uninstrumented directly; their outcomes are captured through the `vet`/`validate`/`finish` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
