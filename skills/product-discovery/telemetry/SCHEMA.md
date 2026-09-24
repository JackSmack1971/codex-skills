# Telemetry schema for product-discovery

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `bb7b4c0f27beb1c931f14d946f5ab881464cf82128b8bc78b85e34e7ae329f8b`

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
calls wired into `SKILL.md`'s Telemetry section. They measure whether this
skill actually separates fact from assumption and narrows toward the
riskiest unknown, rather than just producing a plausible problem statement.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`problem_unclear`, `target_user_unclear`, `desired_outcome_unclear`, `multiple_unclear`) | Which Trigger-and-exclusion dimension was vague at the start of the run. | Lets an improvement agent see whether a particular kind of vagueness (e.g. target user) correlates with weaker downstream evidence/assumption separation. |
| `decision` | `classify_evidence` | `evidence_count` / `assumption_count` | integer | Size of the Workflow-step-3 evidence and assumption lists. | An `assumption_count` far exceeding `evidence_count` on every run may mean the skill is not actually gathering evidence, only guessing. |
| `decision` | `classify_evidence` | `invented_facts_flagged` | boolean | Whether a would-be invented market fact was caught and excluded. | Directly measures compliance with "do not invent market facts." |
| `decision` | `rank` | `assumptions_ranked` | integer | Number of assumptions actually ranked by uncertainty × consequence. | A zero or near-zero count despite many listed assumptions means step 4's ranking is being skipped. |
| `decision` | `rank` | `riskiest_assumption_identified` | boolean | Whether a single riskiest assumption was named. | The skill's stated purpose ("so the riskiest unknown can be tested cheaply") fails silently if this is false. |
| `verification` | `experiments` | `experiments_count` | integer | Number of validation experiments defined in step 5. | Outlier-low counts on high-uncertainty problems suggest under-validation. |
| `verification` | `experiments` | `signals_defined` / `decision_rules_defined` | boolean | Whether success/failure signals and decision rules were both specified. | These are required Output fields; a false rate flags experiments that can't actually be acted on. |
| `run.finished` | `finish` | `open_questions_count` | integer | Count of open questions returned. | High or rising counts indicate the skill is being invoked on inputs it cannot resolve even after discovery. |
| `run.finished` | `finish` | `output_format` | enum (`file`, `inline`) | Whether `PRODUCT_DISCOVERY.md` was written or an inline answer was given. | Confirms the Output section's file/inline branching is followed correctly based on the request. |

An improvement agent should compare `assumption_count` against `evidence_count`
across runs, watch the rate of `riskiest_assumption_identified == false`, and
check whether `experiments_count` stays proportionate to `assumptions_ranked`
to decide whether the Workflow section of `SKILL.md` needs revision.
