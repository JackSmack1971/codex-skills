# Integration guide: imagegen

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
| Before Workflow step 1 (decide top-level mode) | `run.started` | `task_category` (use-case taxonomy slug) |
| After Workflow step 4 (decide execution strategy) | `decision` (`phase=plan`) | `mode`, `intent`, `execution_strategy`, `transparency_requested` |
| After Workflow step 12 (inspect outputs and validate) | `verification` (`phase=validate`) | `subject_match`, `style_match`, `text_accuracy_checked`, `invariants_preserved`, `alpha_validated`, `iteration_count` |
| Before Workflow step 18 (report final saved paths) | `run.finished` | `use_case`, `mode`, `execution_strategy`, `asset_count`, `transparency_used`, `saved_to_workspace` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:184-209` — Use-case taxonomy (exact slugs) — became the `task_category`/`use_case` enum.
- `SKILL.md:96` — Workflow step 1 "Decide the top-level mode: built-in by default... fallback CLI only if explicitly requested" — became `mode`.
- `SKILL.md:97` — Workflow step 2 "Decide the intent: `generate` or `edit`" — became `intent`.
- `SKILL.md:99` — Workflow step 4 "Decide the execution strategy: single asset vs repeated built-in calls vs CLI `generate-batch`" — became `execution_strategy`.
- `SKILL.md:111-112` — Workflow steps 11-12 (transparent-output handling; "Inspect outputs and validate: subject, style, composition, text accuracy, and invariants/avoid items") — became `transparency_requested`, `alpha_validated`, and the four `validate`-phase boolean checks.
- `SKILL.md:113` — Workflow step 13 "Iterate with a single targeted change, then re-check" — became `iteration_count`.
- `SKILL.md:115-116` — Workflow steps 15-16 (move/copy the selected artifact into the workspace; never leave a project-referenced asset only at the default path) — became `saved_to_workspace`.

### Execution candidates

- `scripts/image_gen.py` and `scripts/remove_chroma_key.py` remain uninstrumented directly; their outcomes are captured through the `plan`/`validate`/`finish` events above (`mode`, `alpha_validated`) instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
