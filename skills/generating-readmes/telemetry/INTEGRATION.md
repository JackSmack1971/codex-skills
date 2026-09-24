# Integration guide: generating-readmes

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
this skill's actual Procedure steps (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (`write`/`audit_only`/`no_write`) |
| After step 2 (build repository evidence inventory) | `decision` (`phase=inventory`) | `key_files_inspected`, `secrets_excluded` |
| After step 5 (write or report) | `decision` (`phase=draft`) | `mode`, `sections_covered`, `inferred_items_count` |
| After step 6 (verify before completion) | `verification` (`phase=verify`) | `quality_score`, `min_score_met`, `rerun_count` |
| Before returning the final report | `run.finished` | `mode`, `quality_score`, `tbd_items_count`, `inferred_items_count` |
| When a maintainer later overturns a claim, gap, or score | `user.correction` | `original_quality_score`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:25` — the `--audit-only`/`--no-write`/default `$ARGUMENTS` modes — became `task_category`/`mode`.
- `SKILL.md:38-40` — "Read the generated inventory output before drafting. Directly inspect the most important source files" plus "Never read secret-bearing files" — became `key_files_inspected`/`secrets_excluded`.
- `SKILL.md:48` — the `[INFERRED]` marking rule for unconfirmed conventions — became `inferred_items_count`.
- `SKILL.md:73-87` — the Definition of done's required section list — became the `sections_covered` enum.
- `SKILL.md:58-59` — `readme_quality_check.py --min-score 24` and the one-rerun rule — became the `verify`-phase fields.
- `SKILL.md:67` — "Do not link to governance files that are absent; write `[TBD]`" — became `tbd_items_count`.

### Execution candidates

- `scripts/scan_repo.py` and `scripts/readme_quality_check.py` remain uninstrumented directly; their outcomes are captured through the `inventory`/`verify` events above instead of per-invocation instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
