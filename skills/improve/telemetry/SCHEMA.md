# Telemetry schema for improve

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `58b97ae0c6be0f0579aaef5efb0860eaccb7a2ea7fa9266f38bdab4ef2f2e352`

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
wired into `SKILL.md`'s Telemetry section. They measure this skill's core
job — producing a vetted, execution-ready plan at the requested effort and
focus — not just that an audit ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`audit`, `direction`, `plan`, `review_plan`) | Which Invocation mode was used (`next`/`features`/`roadmap`, `plan <request>`, `review-plan <path>`, or a default audit). | Lets an improvement agent compare finding quality and plan acceptance across the skill's distinct entry points. |
| `decision` | `scope` | `effort` | enum (`quick`, `standard`, `deep`) | Parsed audit effort. | Detects whether effort is being resolved sensibly relative to request size, or defaulting to `standard` too often. |
| `decision` | `scope` | `focus` | enum (`security`, `performance`, `tests`, `architecture`, `dependencies`, `dx`, `docs`, `all`) | Parsed audit focus. | The primary signal for whether findings actually concentrate on the requested focus area. |
| `decision` | `scope` | `branch_scoped` | boolean | Whether `branch` limited the audit to changes since the merge base. | Separates full-repository audits from change-scoped ones when interpreting finding counts. |
| `verification` | `vet` | `candidates_considered` / `candidates_rejected` | integer | Counts from independently reopening every cited location. | A near-zero rejection rate on a large audit suggests the reopen-and-reject vetting step (step 4) is not substantively occurring. |
| `verification` | `vet` | `rejection_reasons` | array of enum (`stale`, `duplicate`, `generic`, `unreachable`, `documented`) | Which of step 4's named rejection categories fired. | Reveals which failure mode (staleness vs. duplication vs. false positives) most often needs tightening in the audit playbook. |
| `verification` | `validate` | `plan_validation_exit_code` | integer | `validate_plan.py` exit code. | A nonzero rate signals plans are being written that don't meet `plan-spec.md`'s contract. |
| `verification` | `validate` | `sensitive_output_flagged` | boolean | Whether `scan_sensitive_output.py` flagged the plan. | Tracks the secret/credential-leak boundary independent of plan-format correctness. |
| `verification` | `validate` | `retry_count` | integer | Repair attempts after a failed validation. | A rising retry rate points at a recurring, fixable defect class in plan generation. |
| `run.finished` | `finish` | `findings_count` / `plans_written` | integer | Final output volume. | Outlier-low counts on a `deep` effort audit suggest under-coverage; trending counts show drift. |
| `user.correction` | — | `correction`, `detail` | string | A maintainer or executing agent later reporting a finding was invalid or a plan step was infeasible/incomplete. | The ground-truth signal for whether this skill's findings and plans were actually actionable — without it, `findings_count` and `plans_written` only show volume, not correctness. |

An improvement agent should aggregate `focus`/`effort` distributions against
`findings_count` and `candidates_rejected` rates, and join `decision`/
`verification` events against later `user.correction` events (same
`run_id`) to see whether the Required-workflow's vetting step (step 4) is
actually catching what it claims to.
