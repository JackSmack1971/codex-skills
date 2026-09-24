# Telemetry schema for systematic-debugging

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `51d2206a224601066743c46d30363573dc3d601626c20b220ef86f00655961ff`

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
job — root-causing failures under the invariant "no permanent fix before
evidence" — not just that a debugging session happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`bug`, `test_failure`, `build_failure`, `regression`, `unexpected_behavior`) | Which class of failure signal triggered the run, per the skill's own Trigger and exclusion. | Lets an improvement agent see whether one failure class systematically produces more inconclusive or partial completions. |
| `verification` | `baseline` | `reproducible` / `intermittent` | boolean | Whether step 1's reproduction succeeded, and whether the failure is intermittent. | Distinguishes cases where a weak diagnosis stems from unreproducible evidence rather than a flawed hypothesis. |
| `verification` | `baseline` | `baseline_captured` | boolean | Whether a pre-change baseline was captured for already-failing tests. | Confirms step 1's regression-distinguishing requirement is actually honored. |
| `decision` | `hypothesis` | `hypothesis_confirmed` | boolean | Whether the falsifiable hypothesis (step 3) was confirmed or refuted. | Core signal for hypothesis quality; a low confirmation rate suggests hypotheses are being formed too speculatively. |
| `decision` | `hypothesis` | `failed_attempts` | integer | Count of refuted hypotheses this run. | Directly tracks the "after three unsuccessful correction attempts" escalation rule; a high average signals the Localize-the-fault guidance needs strengthening. |
| `decision` | `hypothesis` | `scope_expansion_requested` | boolean | Whether broader architectural investigation was proposed after repeated failures. | Confirms the required "ask before expanding scope" checkpoint is being hit rather than silently stacking speculative fixes. |
| `operation` | `correct` | `containment_used` | boolean | Whether a temporary mitigation (Invariant and containment exception) was applied before root-cause correction. | Tracks how often containment substitutes for a real fix, which the skill explicitly says containment does not constitute. |
| `operation` | `correct` | `regression_check_added` | boolean | Whether a durable regression check was added per step 4. | A low rate flags fixes shipped without the regression protection the skill requires "when practical." |
| `operation` | `correct` | `defense_in_depth_added` | boolean | Whether an additional independent boundary check was added. | Tracks adoption of the optional defense-in-depth branch (step 4) versus single-point fixes. |
| `operation` | `correct` | `scope_expansion_flagged` | boolean | Whether an unrelated-refactor scope expansion was surfaced before proceeding. | Confirms step 4's "surface that scope expansion before proceeding" rule is followed rather than silently bundled in. |
| `verification` | `verify` | `symptom_resolved` / `regression_check_passes` / `surrounding_checks_clean` | boolean | The three concrete completion checks from step 5. | Each is one of the skill's own stated completion-criteria items; false values pinpoint exactly which completion bar was not met. |
| `verification` | `verify` | `completion_status` | enum (`complete`, `partial`, `inconclusive`) | Overall completion verdict per step 5. | The primary outcome signal for whether the workflow reached a defensible stop. |
| `run.finished` | `finish` | `completion_status`, `failed_attempts`, `containment_used` | enum / integer / boolean | Final run summary. | Cross-run aggregation of diagnostic reliability without re-reading each session. |
| `user.correction` | — | `original_completion_status`, `correction` | enum (`complete`, `partial`, `inconclusive`) / enum (`root_cause_incorrect`, `regression_reintroduced`, `fix_ineffective`) | A maintainer later reporting the diagnosis or fix did not hold up. | The ground-truth signal for whether a `completion_status=complete` run was actually correct. |

An improvement agent should track the `completion_status` distribution
against `failed_attempts` (many failed attempts still ending `complete` may
mean root causes are found only after excess churn) and join `verification`
(`phase=verify`) against later `user.correction` events to estimate how
often "complete" runs are later found wrong — a signal for tightening the
step-5 completion criteria.
