# Telemetry schema for imagegen

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `f5b932028b65b839164077ea0c4851b9d4ab65d812214582163cb7b8c17164ef`

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
calls wired into `SKILL.md`'s Telemetry section. They are the fields an
improvement agent should read to judge whether this skill picks the right
mode/strategy and actually validates its own output, not just that a run
happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (the 19 use-case taxonomy slugs) | Which generate/edit use case the request was classified as. | Lets an improvement agent see which use cases are actually requested and whether findings/failures cluster on a specific slug. |
| `decision` | `plan` | `mode` | `"built_in"` \| `"cli_fallback"` | Which top-level mode was used. | The skill's own rule is built-in-by-default; a rising `cli_fallback` rate not explained by explicit user requests signals drift from the stated default. |
| `decision` | `plan` | `intent` | `"generate"` \| `"edit"` | Whether the request was treated as a new image or an edit. | Validates the Decision-tree intent classification against downstream outcomes. |
| `decision` | `plan` | `execution_strategy` | `"single_asset"` \| `"repeated_built_in_calls"` \| `"cli_generate_batch"` | How multi-asset requests were executed. | Confirms the skill isn't misusing `n` as a substitute for distinct prompts, per its own execution-strategy rule. |
| `decision` | `plan` | `transparency_requested` | boolean | Whether a transparent-background output was requested. | Segments the transparency workflow (chroma-key vs. CLI true transparency) for separate quality tracking. |
| `verification` | `validate` | `subject_match` / `style_match` / `text_accuracy_checked` / `invariants_preserved` | boolean | Whether Workflow step 12's four named checks were performed and passed. | A persistent `false`/absent pattern means the inspect-and-validate step is pro forma rather than substantive. |
| `verification` | `validate` | `alpha_validated` | boolean or null | Whether the chroma-key alpha result was validated (null when transparency wasn't requested). | Measures whether the transparent-image validation step (alpha channel, transparent corners, no fringe) is actually being run. |
| `verification` | `validate` | `iteration_count` | integer | Number of single-targeted-change iterations before acceptance. | High iteration counts on a use case indicate the initial prompt-augmentation or mode choice needs improvement. |
| `run.finished` | `finish` | `use_case` / `mode` / `execution_strategy` | mixed | Final classification and path taken. | Cross-run aggregation surface for the fields above. |
| `run.finished` | `finish` | `asset_count` | integer | Number of assets/variants produced. | Distinguishes single-asset from batch runs when interpreting other counts. |
| `run.finished` | `finish` | `transparency_used` | boolean | Whether a transparency workflow (chroma-key or CLI) was actually exercised. | Cross-checked against `transparency_requested` to catch silently dropped transparency requests. |
| `run.finished` | `finish` | `saved_to_workspace` | boolean | Whether the final asset was moved/copied into the project workspace. | Directly measures the "never leave a project-referenced asset only at the default path" rule. |

An improvement agent should aggregate `mode` and `execution_strategy`
distributions against `task_category`, watch `cli_fallback` rate for drift
from the stated built-in-by-default policy, and track `iteration_count` and
`alpha_validated` failure rates as leading indicators that the prompting or
transparency guidance in `SKILL.md` needs revision.
