# Telemetry schema for grill-me

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `c459e2c039c981c3f211926472d6c6fbf94fdb66d1bf7bba57ad198ff1bbc614`

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

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. Because this skill is a
compatibility alias that delegates the whole session to `grilling`'s
interrogate-then-confirm shape, the fields mirror what an improvement agent
needs to judge that delegated interview, tagged as reached through the
explicit `/grill-me` entry point.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`plan`, `design`) | Whether the stress-test target was a plan or a design. | Lets an improvement agent see whether the explicit `/grill-me` entry point skews toward one target type, and compare outcomes against the same taxonomy on `grilling`. |
| `decision` | `interrogate` | `questions_asked` | integer | Number of questions posed in the session. | A chronically low count on a complex plan/design suggests the interrogation stops short of "materially sharper." |
| `decision` | `interrogate` | `assumptions_challenged` / `constraints_exposed` / `alternatives_tested` | integer | Counts tied directly to this skill's own stated actions ("Challenge assumptions, expose missing constraints, test alternatives"). | Zero counts across many sessions indicate the skill is running through the motions without doing the stated work. |
| `decision` | `interrogate` | `answer_sources` | array of enum (`codebase_explored`, `user_asked`) | Whether answers came from codebase exploration or the user. | Tracks whether the delegate is actually exploring the codebase before asking, per its own instruction. |
| `verification` | `confirm` | `materially_sharper` | boolean | Whether the session's own bar ("until the plan or design is materially sharper") was met. | A self-check that is always `true` regardless of session length is a sign the gate is not substantive. |
| `verification` | `confirm` | `shared_understanding_confirmed` | boolean | Whether the user explicitly confirmed shared understanding before enactment. | Directly measures adherence to the "do not enact until confirmed" gate. |
| `run.finished` | `finish` | `questions_asked` / `materially_sharper` / `shared_understanding_confirmed` | mixed | Session summary. | Lets an improvement agent trend session depth and confirmation-gate adherence over time. |
| `user.correction` | — | `correction`, `detail` | string | A user later rejecting a recommended answer or naming a missed branch/constraint. | The ground-truth signal for whether this skill's recommendations and coverage were actually sound. |

An improvement agent should compare `questions_asked` and the challenge/
expose/test counts against session outcomes (confirmed vs. abandoned), and
watch `user.correction` rate as the leading indicator that the alias's
interrogation is under-covering plans or designs.
