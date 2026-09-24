# Telemetry schema for visual-plan

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `91946ef35e6a861e734c0fd31cdeccb9489e8b87e4191e28db6efd5250667fc7`

## Event classes

- `run.started`, `run.finished`
- `skill.invocation`
- `precondition`
- `decision`
- `operation`
- `verification`
- `failure`, `retry`
- `user.correction`, `agent.error`
- `eval.result`, `lesson.candidate`
- `hook.observation`, `usage`

## Attribution

- `semantic`: target-owned event with target fingerprint.
- `confirmed`: imported/correlated evidence known to exercise this skill.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. They measure whether the
skill picks the right visual surface and actually self-reviews before
publishing, not just that a plan was produced.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | `"fresh_plan"` \| `"from_existing_plan"` | Whether the run started from scratch or from an existing Codex/Markdown/pasted plan. | Lets an improvement agent check whether `from_existing_plan` runs correctly preserve prior content via `contentPatches` rather than a full replacement. |
| `decision` | `choose_surface` | `surface_mode` | enum (`document_only`, `ui_first`, `prototype_first`, `design_first`, `visual_intake`) | Which visual surface was chosen for the task. | Reveals whether the skill defaults to one surface regardless of task shape, or genuinely differentiates backend/architecture work from product-screen work. |
| `decision` | `choose_surface` | `tool_mapped` | enum (`create-visual-plan`, `create-ui-plan`, `create-prototype-plan`, `create-plan-design`, `create-visual-questions`) | Which plan-service tool the chosen surface routed to. | Confirms `surface_mode` and the actual tool call stay in sync per the reference's own mapping table. |
| `verification` | `self_review` | `factual_grounding_checked` / `accessibility_checked` | boolean | Whether the required self-review dimensions were actually checked. | A persistent false rate means step 5 (self-review) is being skipped rather than performed. |
| `verification` | `self_review` | `hard_to_reverse_decisions_flagged` | integer | Count of hard-to-reverse decisions surfaced with a recommended default. | Tracks whether the "surface hard-to-reverse decisions" requirement is substantive, not pro forma. |
| `verification` | `self_review` | `unresolved_questions_count` | integer | Count of unresolved questions raised. | High or rising counts on repeated runs may indicate the skill is being invoked before enough repository evidence exists. |
| `run.finished` | `finish` | `publish_mode` | enum (`hosted`, `local_files`) | Which publication path was used. | Verifies private/local-only material never gets a hosted URL, per the Boundaries section. |
| `run.finished` | `finish` | `approval_requested` | boolean | Whether approval was requested before implementation. | A false value on non-trivial work is a direct violation of "request approval before implementation." |
| `user.correction` | — | `correction` | enum (`default_rejected`, `scope_changed`, `surface_mode_wrong`) | How a reviewer's anchored feedback overturned this run's output. | The ground-truth signal for whether the chosen surface and recommended defaults actually matched reviewer intent. |

An improvement agent should watch whether `surface_mode` distribution matches
the task shapes described in `SKILL.md`'s opening paragraph, track
`unresolved_questions_count` and `hard_to_reverse_decisions_flagged` trends
against later `user.correction` events, and flag any `publish_mode: hosted`
run whose `task_category`/content should have stayed local.
