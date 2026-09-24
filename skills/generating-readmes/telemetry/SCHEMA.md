# Telemetry schema for generating-readmes

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `ef77a67f3723ef94a5a2bbd925b512bdd15c60f4df0346f1d4944c4be4c31a3d`

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

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether the README
is actually grounded in repository evidence and meets the skill's own
Definition of done, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`write`, `audit_only`, `no_write`) | Which `$ARGUMENTS` mode this run used. | Lets an improvement agent see whether one mode (e.g. `audit_only`) surfaces more gaps or corrections than the others. |
| `decision` | `inventory` | `key_files_inspected` | integer | Source files directly inspected beyond the generated inventory, per step 2. | A near-zero count on a nontrivial repository suggests claims are being drafted from the inventory summary alone rather than from real evidence. |
| `decision` | `inventory` | `secrets_excluded` | boolean | Whether secret-bearing files were correctly excluded from evidence. | Directly checks the Safety rules' "do not expose secrets" requirement. |
| `decision` | `draft` | `sections_covered` | array of enum (`quickstart`, `features`, `architecture`, `directory_structure`, `configuration`, `command_center`, `testing_verification`, `troubleshooting`, `stack_inventory`, `reproducibility`, `contribution_governance`) | Which Definition-of-done sections the draft actually included. | Directly measures whether the skill follows its own required section checklist; missing sections are concrete gaps to fix in the Procedure. |
| `decision` | `draft` | `inferred_items_count` | integer | Claims marked `[INFERRED]` in the draft. | Tracks reliance on inference versus hard evidence; a rising trend on well-documented repositories suggests step 2's inventory usage is weakening. |
| `verification` | `verify` | `quality_score` / `min_score_met` | integer / boolean | `readme_quality_check.py` result against the required minimum of 24. | The primary pass/fail signal for whether the README met the skill's own bar before delivery. |
| `verification` | `verify` | `rerun_count` | integer | Fix-and-rerun cycles per step 6's "rerun the quality check once." | A rerun that still fails after one fix cycle means the underlying gap needs a Procedure fix, not another retry. |
| `run.finished` | `finish` | `tbd_items_count` | integer | Remaining `[TBD]` items at delivery. | High or rising counts indicate the repository lacks evidence the skill needs — a signal to tighten expectations or gather more input rather than fabricate. |
| `user.correction` | — | `original_quality_score`, `correction` | integer / string | A maintainer later correcting an `[INFERRED]` claim, dismissing a reported gap, or disputing the quality score. | The ground-truth signal for whether this run's grounding and scoring held up in practice. |

An improvement agent should aggregate `sections_covered` across runs to find
which Definition-of-done section is most often missing, and join `verify`
outcomes against later `user.correction` events to see whether a high
`quality_score` reliably predicts no downstream corrections.
