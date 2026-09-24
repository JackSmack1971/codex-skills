# Integration guide: design-md-ideator

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
| Before step 1 | `run.started` | `task_category` (`create`/`refine`/`reconstruct`/`validate`) |
| After step 1 (discover existing design evidence) | `decision` (`phase=discover`) | `evidence_sources`, `ledger_classifications` |
| After step 5 (present the decision ledger) | `decision` (`phase=ledger`) | `token_groups_nonempty`, `unresolved_assumptions`, `recommended_defaults` |
| After step 7 (validate, fix, and revalidate) | `verification` (`phase=validate`) | `exit_code`, `retry_count`, `profile` |
| Before step 8 (deliver) | `run.finished` | `sections_completed`, `validation_exit_code`, `assumptions_disclosed` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:14` — "all five token groups are non-empty; all eight canonical sections are present" — became `token_groups_nonempty` and `sections_completed`.
- `SKILL.md:55-58` — the `confirmed`/`recommended`/`assumed`/`conflict` ledger labels — became `ledger_classifications`.
- `SKILL.md:46-51` — the ordered evidence-discovery list (existing DESIGN.md/tokens, screenshots/brand, components, user requirements) — became the `evidence_sources` enum.
- `SKILL.md:78-85` — the five token-decision categories (colors, typography, spacing, rounded, components) — became the `token_groups_nonempty` enum.
- `SKILL.md:126` — "Stop questioning when every required field is either confirmed or an explicitly disclosed recommended default" — became `unresolved_assumptions`/`recommended_defaults`.
- `SKILL.md:142-163` — the validate/fix/revalidate loop and its `--profile strict` invocation — became the `validate`-phase `verification` fields.

### Execution candidates

- `scripts/validate_design_md.py` is folded into the `validate`-phase `verification` event (its exit code and repair cycles) rather than instrumented per-invocation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
