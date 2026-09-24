# Integration guide: mvp-scope

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
| Before step 1 | `run.started` | `task_category` (input form) |
| After step 3 (classify items) | `decision` (`phase=classify`) | `must_have_count`, `should_have_count`, `later_count`, `wont_build_count` |
| After step 4 (remove speculative scope) | `decision` (`phase=trim`) | `trimmed_categories`, `items_removed`, `safety_constraint_preserved` |
| After step 5 (record risks/unresolved/slice) | `verification` (`phase=finalize`) | `risks_count`, `unresolved_decisions_count`, `end_to_end_slice_defined` |
| Before returning output | `run.finished` | `must_have_count`, `wont_build_count`, `promotion_criteria_stated` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:4` — compatibility: "Requires a product problem, desired outcome, constraints, or feature list." — became the `task_category` enum.
- `SKILL.md:16` — step 3 classification into Must have/Should have/Later/Explicitly won't build — became the `classify`-phase counts.
- `SKILL.md:17-18` — step 4 removal list (speculative flexibility, premature scale, admin, multi-tenancy, extensibility, infrastructure) — became the `trimmed_categories` enum.
- `SKILL.md:19` — step 5 "risks, unresolved decisions, and the smallest end-to-end slice" — became the `finalize`-phase fields.
- `SKILL.md:23,25` — Output's "definition of done" and "evidence that would justify promoting a deferred item" — became `promotion_criteria_stated`.
- `SKILL.md:29-30` — Boundary rule against silently dropping safety/accessibility/compliance/data-loss requirements — became `safety_constraint_preserved`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
