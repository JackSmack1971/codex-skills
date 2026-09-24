# Telemetry schema for database-migrations

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `00c920ef9eac195c2f16b04d10c4046e27d0c24340d2c2173c3926eaeee8a482`

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
- `correlated`: hook-observed execution evidence (tool calls, commands, exit codes) automatically attached to the semantic run that was open in the same session when it fired; included in analysis by default, but is a best-effort session-scoped join, not proof the tool call belongs to this skill's own logic.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence outside any open run; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether this
skill's change classification and safety guarantees hold up, not just that
a migration plan was produced.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`plan`, `implement`, `review`) | Which of the description's three actions (plan, implement, or review) was requested. | Lets an improvement agent check whether `implement` runs skip planning rigor that `plan`-only runs perform. |
| `decision` | `classify` | `change_type` | enum (`additive`, `backfill`, `rewrite`, `rename`, `constraint`, `destructive`) | Step 2's change classification. | The primary risk-tier signal; drives how much scrutiny the rest of the run should apply. |
| `decision` | `classify` | `destructive_approval_required` | boolean | Whether the classification triggered the Boundary's explicit-approval requirement. | Directly measures whether the Boundary's core safety gate actually engages when `change_type` is `destructive`. |
| `decision` | `sequence` | `expand_contract_used` | boolean | Whether step 3's expand/contract sequencing was applied. | Tracks whether compatibility-sensitive changes actually get the sequencing step 3 requires, or skip straight to a single-phase change. |
| `decision` | `sequence` | `compatibility_window_defined` | boolean | Whether an old/new application overlap window was stated. | The skill's stated purpose is preserving compatibility during overlap; a missing window on a multi-phase change is a concrete gap. |
| `verification` | `safety` | `idempotent` / `batching_defined` / `failure_handling_defined` / `observability_defined` | boolean | Whether step 4's batching, locks, idempotency, observability, and failure-handling requirements were each addressed. | Each is individually named in step 4; persistent `false` values on any one flags a recurring safety-checklist gap. |
| `verification` | `verify` | `rollback_strategy` | enum (`rollback`, `forward_fix`) | Step 5's stated recovery approach. | Confirms step 5 always names a concrete recovery path rather than leaving it implicit. |
| `verification` | `verify` | `backup_assumption_stated` | boolean | Whether step 5's backup assumptions were stated. | Directly checks step 5 compliance; a missing statement undermines the recovery plan's credibility. |
| `verification` | `verify` | `verification_checks_count` | integer | Verification queries/checks defined in step 5. | A zero count means the plan has no way to confirm success — a critical completeness gap for irreversible-adjacent work. |
| `run.finished` | `finish` | `destructive` | boolean | Whether the finished plan was for a destructive change. | Lets an improvement agent isolate the highest-risk subset of runs for closer review. |
| `user.correction` | — | `original_change_type`, `correction`, `new_change_type` | string | A reviewer later reclassifying the change, revoking an approval, or finding the stated rollback path infeasible. | The ground-truth signal for calibration — without it, `change_type`/`rollback_strategy` only show what the skill claimed, not whether it was accurate. |

An improvement agent should join `decision` (`phase=classify`) events
against later `user.correction` events (same `run_id`) to compute how often
a declared `change_type` is later revised — especially any case where a
non-`destructive` classification is corrected to `destructive` after the
fact, which is the single highest-value signal for revising step 2's
classification guidance.
