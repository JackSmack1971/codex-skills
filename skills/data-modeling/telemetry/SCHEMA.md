# Telemetry schema for data-modeling

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `50bef9511dc664c24b170a66553377f77ff0c80b0a44de211f548c8cc2bf8ac6`

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
skill's constraints, indexes, and trade-offs are actually justified by
stated behavior, not just that a model was produced.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`design`, `review`) | Whether a new model was designed or an existing one reviewed, per the skill's own description. | Lets an improvement agent check whether review runs surface different integrity issues than fresh designs. |
| `decision` | `constrain` | `entities_count` | integer | Entities/value objects modeled in step 1-2. | Baseline scale metric; near-zero on a non-trivial domain flags under-modeling. |
| `decision` | `constrain` | `uniqueness_constraints_count` / `foreign_keys_count` | integer | Uniqueness and foreign-key constraints defined per step 2. | Directly measures step 2 compliance; chronically zero counts on multi-entity models suggest constraints are being skipped. |
| `decision` | `constrain` | `soft_delete_used` | boolean | Whether deletion behavior (step 2) uses soft deletion vs. hard deletion. | Surfaces a load-bearing lifecycle decision that later migration and audit work depends on. |
| `decision` | `index` | `indexes_added_count` | integer | Indexes added per step 3. | Tracks output volume against read/write-pattern justification. |
| `decision` | `index` | `justified_by_access_pattern` | boolean | Whether every added index traces to a stated read/write pattern. | Directly checks the Boundary's "do not add ... for hypothetical future use" rule applied to indexes. |
| `verification` | `tradeoffs` | `normalization_choice` | enum (`normalized`, `denormalized`, `mixed`) | Step 4's normalization/denormalization outcome. | Tracks which trade-off the skill defaults to across domains, useful for spotting a one-size-fits-all bias. |
| `verification` | `tradeoffs` | `concurrency_assumptions_stated` | boolean | Whether step 4's concurrency assumptions were stated. | A skipped concurrency statement is a common, hard-to-detect gap this field surfaces directly. |
| `verification` | `tradeoffs` | `transaction_boundaries_defined` | boolean | Whether step 4's transaction boundaries were defined. | Same rationale — validates the self-check is substantive rather than pro forma. |
| `run.finished` | `finish` | `unresolved_domain_questions` | integer | Count of unknown domain rules marked as questions in the output. | High or rising counts indicate the skill is being invoked on domains it cannot fully resolve — a signal for tightening the Trigger/exclusion boundary. |
| `user.correction` | — | `original_decision`, `correction`, `entity` | string | A later reviewer changing a normalization choice or adding/removing/revising a constraint or index this run produced. | The ground-truth signal for calibration — without it, `decision`/`verification` fields only show what the skill chose, not whether it held up. |

An improvement agent should track the distribution of `normalization_choice`
and the rate of nonzero `unresolved_domain_questions` across runs, and join
`decision` events against later `user.correction` events (same `run_id`) to
see whether particular constraint or indexing choices are systematically
revised.
