---
name: visual-plan
description: "Turn text plans into interactive visual plans with diagrams, file maps, annotated code, and review artifacts."

---

# Agent-Native Plans

Use `/visual-plan` when a plan benefits from a reviewable structured artifact:
UI, workflows, architecture, data flow, options, or risky multi-file work.
Start from an existing Codex/Markdown/pasted plan when one exists. Skip it for
trivial, unambiguous work.

## Required behavior

- Research real files and reusable patterns first; planning is read-only.
- Publish a standalone structured Agent-Native Plan, never an inline plan.
- Choose document-only, UI-first, prototype-first, design-first, or
  visual-intake mode from the task.
- Read the live block catalog before authoring structured blocks.
- Ground paths, symbols, data, diagrams, and examples in repository evidence.
- Surface hard-to-reverse decisions and unresolved questions with recommended
  defaults; request approval before implementation.
- Read the relevant reference before authoring wireframes, canvas, or document
  content, and inspect rendered UI when a browser is available.
- Keep private material local or org/login-gated; never expose secrets or guess
  hosted/local plan URLs.

## Workflow and stop conditions

Inspect → choose surface → load block schema → draft → self-review → publish
and hand off. Stop when required facts, connector/schema validation,
authentication, or approval is unavailable instead of inventing details.

Detailed workflow, tool guidance, privacy, comment anchors, visibility,
sharing, setup, and examples: [entrypoint guidance](references/entrypoint-guidance.md).
Read these authoritative references as needed: [wireframe](references/wireframe.md),
[canvas](references/canvas.md), [document quality](references/document-quality.md),
and [exemplar](references/exemplar.md).

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before "Inspect", start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<fresh_plan|from_existing_plan>" --invocation explicit)
   ```
2. After "choose surface", record the surface decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase choose_surface \
     --evidence-json '{"surface_mode":"<document_only|ui_first|prototype_first|design_first|visual_intake>","tool_mapped":"<create-visual-plan|create-ui-plan|create-prototype-plan|create-plan-design|create-visual-questions>"}'
   ```
3. After "self-review", record the review check:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase self_review --outcome <success|failure> \
     --evidence-json '{"factual_grounding_checked":<true|false>,"accessibility_checked":<true|false>,"hard_to_reverse_decisions_flagged":<N>,"unresolved_questions_count":<N>}'
   ```
4. Before "publish and hand off", close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"surface_mode":"<document_only|ui_first|prototype_first|design_first|visual_intake>","publish_mode":"<hosted|local_files>","unresolved_questions_count":<N>,"approval_requested":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g. `connector_unavailable`,
   `missing_required_facts`, `auth_unavailable`) when the workflow stopped
   under a stop condition instead of publishing a plan.

If a reviewer's anchored feedback later overturns a hard-to-reverse decision
or recommended default this run surfaced, record it so plan quality is
visible without re-running the skill:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"correction":"<default_rejected|scope_changed|surface_mode_wrong>"}'
```
