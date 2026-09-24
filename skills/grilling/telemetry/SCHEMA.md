# Telemetry schema for grilling

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `b57ab5d31081ba7ec4daaf5da6fe8838b94209146a1429dd871ac127125b015f`

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
one-question-at-a-time interview actually follows its own five bullet rules,
not just that a session happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`plan`, `design`) | Whether the stress-test target was a plan or a design. | Lets an improvement agent compare interview depth and outcomes by target type. |
| `decision` | `interrogate` | `questions_asked` | integer | Number of questions posed, one at a time. | Outlier-low counts on a complex plan/design suggest the interview is cut short. |
| `decision` | `interrogate` | `branches_resolved` | integer | Design/plan branches walked in dependency order. | Directly measures adherence to "walk each design branch in dependency order, resolving decisions before dependent questions." |
| `decision` | `interrogate` | `questions_without_recommendation` | integer | Questions posed without a recommended answer attached. | Should be near zero; a rising count is drift away from "give a recommended answer with every question." |
| `decision` | `interrogate` | `answer_sources` | array of enum (`codebase_explored`, `user_asked`) | Whether each answer came from codebase exploration or the user. | Validates "explore the codebase when it can answer the question instead of asking the user" is actually happening, not just asserted. |
| `verification` | `confirm` | `shared_understanding_confirmed` | boolean | Whether the user explicitly confirmed shared understanding. | Directly measures the "do not enact the plan until the user confirms" gate. |
| `verification` | `confirm` | `plan_enacted` | boolean | Whether enactment proceeded after confirmation. | Flags any case where enactment happened without a confirmed gate. |
| `run.finished` | `finish` | `questions_asked` / `branches_resolved` / `shared_understanding_confirmed` | mixed | Session summary. | Lets an improvement agent trend interview depth and gate adherence across many sessions. |
| `user.correction` | — | `correction`, `detail` | string | A user later rejecting a recommended answer or naming a missed branch. | The ground-truth signal for whether recommendations and branch coverage were actually sound. |

An improvement agent should watch `questions_without_recommendation` and
`branches_resolved` for drift away from the stated five rules, and join
`decision` events against later `user.correction` events (same `run_id`) to
see whether recommended answers hold up.
