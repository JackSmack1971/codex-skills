# Telemetry schema for visual-recap

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `c681f0d84f7d716f8a1e047d6ca89e3af8b70cac6a09c15afb0b2f59c43cd388`

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
recap is actually derived mechanically from the diff and kept within its
own stated bounds, not just that a recap was produced.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`pr`, `branch`, `commit`, `diff`) | Which work-unit form the recap was derived from. | Lets an improvement agent check whether one input form (e.g. bare `diff`) systematically produces thinner inventories. |
| `decision` | `inventory` | `change_surfaces` | array of enum (`ui_states`, `routes`, `roles`, `files`, `schemas`, `apis`, `shared_abstractions`) | Which Required-behavior inventory categories were actually covered. | Directly measures whether the mandatory pre-authoring inventory is substantive or partial. |
| `decision` | `inventory` | `key_change_tabs_count` | integer | Number of key-change tabs planned. | Values outside the skill's own 3–8 budget signal either under-coverage or a recap turning into a raw diff dump. |
| `operation` | `author` | `block_types_used` | array of enum (`data-model`, `api-endpoint`, `file-tree`, `diff`, `annotated-code`) | Which structured block types were built. | Verifies blocks are built from the categories the skill itself names, not an ad hoc subset. |
| `operation` | `author` | `wireframe_used` / `wireframe_variant` | boolean / enum (`before_after`, `after_only`, `sequence`, `none`) | Whether a wireframe was used and which variant. | Confirms rendered UI changes get the right wireframe treatment (before/after, additive, or stateful/responsive) rather than a default. |
| `verification` | `validate` | `block_catalog_validated` | boolean | Whether the live block catalog/schema was checked before authoring. | A false value on a published recap is a direct violation of "read the live block catalog before authoring." |
| `verification` | `validate` | `secrets_redacted` | boolean | Whether secret-looking values were redacted before publish. | The primary safety signal for this skill; any false value on a published recap is a serious finding. |
| `verification` | `validate` | `tabs_within_budget` | boolean | Whether tab count and excerpt length stayed within the stated budgets. | Tracks whether the "lean but not skeletal" bound is actually enforced. |
| `run.finished` | `finish` | `publish_mode` | enum (`hosted`, `local_files`) | Which publication path was used. | Verifies local-files mode is honored when required, mirroring visual-plan's own signal. |
| `user.correction` | — | `correction` | enum (`annotation_disputes_grounding`, `missing_change_flagged`, `wireframe_state_wrong`) | How a reviewer's routed-back annotation overturned this run's recap. | The ground-truth signal for whether the recap's grounding actually matched the real diff. |

An improvement agent should watch whether `change_surfaces` coverage and
`key_change_tabs_count` drift outside the skill's own stated budgets, check
`secrets_redacted` for any false value as a priority finding, and join
`operation`/`verification` events against later `user.correction` events to
see which `block_types_used` or `wireframe_variant` choices most often get
disputed.
