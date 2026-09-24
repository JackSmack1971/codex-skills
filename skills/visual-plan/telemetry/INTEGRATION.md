# Integration guide: visual-plan

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
this skill's actual Inspect → choose surface → load block schema → draft →
self-review → publish arrow-workflow (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before "Inspect" | `run.started` | `task_category` (`fresh_plan`/`from_existing_plan`) |
| After "choose surface" | `decision` (`phase=choose_surface`) | `surface_mode`, `tool_mapped` |
| After "self-review" | `verification` (`phase=self_review`) | `factual_grounding_checked`, `accessibility_checked`, `hard_to_reverse_decisions_flagged`, `unresolved_questions_count` |
| Before "publish and hand off" | `run.finished` | `surface_mode`, `publish_mode`, `unresolved_questions_count`, `approval_requested` |
| When a reviewer's anchored feedback overturns the plan | `user.correction` | `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11` — "Start from an existing Codex/Markdown/pasted plan when one exists. Skip it for trivial, unambiguous work." — became `task_category`.
- `SKILL.md:18-19` — "Choose document-only, UI-first, prototype-first, design-first, or visual-intake mode from the task." plus `references/entrypoint-guidance.md:29-34`'s tool mapping — became `surface_mode`/`tool_mapped`.
- `SKILL.md:22-23` — "Surface hard-to-reverse decisions and unresolved questions with recommended defaults; request approval before implementation." — became `hard_to_reverse_decisions_flagged`, `unresolved_questions_count`, `approval_requested`.
- `SKILL.md:26-28` — "Keep private material local or org/login-gated; never expose secrets or guess hosted/local plan URLs." plus the entrypoint guidance's local-files-mode boundary — became `publish_mode`.
- `SKILL.md:31-33` — the Inspect → ... → publish workflow and its stop conditions — became the wired event sequence and `--failure-class` values.
- `references/document-quality.md:174` — "Before handoff, open the plan and check it." — became `factual_grounding_checked`/`accessibility_checked`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument (the plan-service tool calls it drives are external MCP tools, not local scripts).

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
