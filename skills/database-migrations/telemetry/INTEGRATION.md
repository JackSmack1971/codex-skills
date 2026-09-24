# Integration guide: database-migrations

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
this skill's actual numbered Workflow steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (`plan`\|`implement`\|`review`) |
| After step 2 (classify the change) | `decision` (`phase=classify`) | `change_type`, `destructive_approval_required` |
| After step 3 (expand/contract sequencing) | `decision` (`phase=sequence`) | `expand_contract_used`, `compatibility_window_defined` |
| After step 4 (batching, locks, idempotency, observability, failure handling) | `verification` (`phase=safety`) | `idempotent`, `batching_defined`, `failure_handling_defined`, `observability_defined` |
| After step 5 (verification, rollback, backup) | `verification` (`phase=verify`) | `rollback_strategy`, `backup_assumption_stated`, `verification_checks_count` |
| Before returning output | `run.finished` | `change_type`, `destructive`, `rollback_strategy`, `verification_checks_count` |
| When a reviewer later reclassifies the change | `user.correction` | `original_change_type`, `correction`, `new_change_type` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the reclassification-rate analysis an improvement agent should run over
these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — the frontmatter description "Plan, implement, or review safe persistent schema changes" — became the `task_category` enum.
- `SKILL.md:27-29` — "classify the change as additive, backfill, rewrite, rename, constraint, or destructive" — became the `change_type` enum.
- `SKILL.md:30-31` — "Use expand/contract sequencing when compatibility requires it: add, deploy compatible code, backfill safely, verify, then contract" — became `expand_contract_used`/`compatibility_window_defined`.
- `SKILL.md:32-33` — "Define batching, locks, transaction limits, idempotency, observability, and failure handling" — became the `safety`-phase `verification` fields.
- `SKILL.md:34-35` — "State verification queries/checks, rollback or forward-fix strategy, and backup assumptions before applying anything" — became the `verify`-phase `verification` fields.
- `SKILL.md:39-41` — the Boundary section (no destructive migration without explicit approval; never promise rollback when irreversible) — became `destructive_approval_required` and the `user.correction` block.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
