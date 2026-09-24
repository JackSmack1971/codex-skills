# Telemetry schema for architecture

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `721c4be7f1ad06f3e06647cc9287cdafd41392b9f1c6c821a482322ad8e5d6e2`

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
job — a well-supported decision that holds up over time — not just that a
run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`adr`, `evaluation`, `component_design`) | Which Modes-section mode was invoked. | Lets an improvement agent check whether one mode systematically produces weaker decisions or thinner alternative analysis. |
| `decision` | `decide` | `status` | enum (`Proposed`, `Accepted`, `Deprecated`, `Superseded`) | The ADR/decision status the run produced. | The primary artifact-state signal; combined with `user.correction`, shows how often initial status holds. |
| `decision` | `decide` | `options_considered_count` | integer | Number of alternatives evaluated. | A count of 1 violates the Quality bar's "name credible alternatives" requirement; trending low counts flag shallow analysis. |
| `decision` | `decide` | `do_nothing_considered` | boolean | Whether "changing nothing" was named as an option. | Directly checks Quality bar item 2, which explicitly requires this option; a persistent `false` on non-trivial decisions is a gap. |
| `verification` | `quality_bar` | `constraints_stated` | boolean | Whether functional/non-functional constraints were stated. | Checks Quality bar item 1 is substantive, not skipped. |
| `verification` | `quality_bar` | `invalidation_conditions_stated` | boolean | Whether the run stated what would invalidate the decision. | Checks Quality bar item 3; missing invalidation conditions make a decision unfalsifiable and harder to revisit later. |
| `verification` | `quality_bar` | `facts_assumptions_separated` | boolean | Whether facts, assumptions, and recommendations were kept distinct. | Checks Quality bar item 4; conflation here is a common failure mode this field surfaces directly. |
| `run.finished` | `finish` | `action_items_count` | integer | Number of action items in the ADR's Action Items section. | A recommendation with zero action items is often incomplete; tracks whether output stays actionable. |
| `user.correction` | — | `original_status`, `new_status`, `reason` | string | A decider later changing the ADR's own `Status` field (e.g. `Accepted` → `Deprecated`/`Superseded`, or rejecting a `Proposed` ADR). | The ground-truth signal for calibration — the ADR template's own status lifecycle is the skill's built-in correction mechanism, so capturing transitions shows how often initial recommendations stick. |

An improvement agent should join `decision` events against later
`user.correction` events (same `run_id`) to compute how often each
`task_category` value's initial `status` survives, and watch
`options_considered_count`/`do_nothing_considered` for drift toward
single-option, foregone-conclusion decisions that violate the Quality bar.
