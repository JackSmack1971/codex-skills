# Telemetry schema for product-spec

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `146b12215cfca5be33a389be6abb5c1043730e24dd72c540711c342c738f59da`

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
skill actually produces a verifiable, complete behavioral contract, not just
a document with the right section headings.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`new_feature`, `existing_system_extension`) | Whether the feature belongs to an existing system (per the `compatibility` line) or is greenfield. | Lets an improvement agent see whether specs for existing-system extensions systematically miss repository/domain context. |
| `decision` | `define_states` | `functional_requirements_count` | integer | Number of functional requirements defined in step 2. | Outlier-low counts on complex features suggest under-specification. |
| `decision` | `define_states` | `states_covered` | array of enum (`loading`, `empty`, `success`, `failure`, `retry`, `recovery`) | Which step-2 observable states were actually defined. | Directly measures whether the skill follows its own required states list; missing states are concrete gaps. |
| `decision` | `non_functional` | `permissions_defined` | boolean | Whether permissions were addressed in step 3. | The Output contract requires a Permissions section; a false rate flags a silently skipped requirement. |
| `decision` | `non_functional` | `analytics_events_count` | integer | Number of analytics events specified. | A chronically zero count on features with user-facing behavior suggests the skill is skipping the analytics requirement. |
| `decision` | `non_functional` | `operational_constraints_flagged` | boolean | Whether operational constraints were captured. | Confirms step 3's non-functional/operational coverage is substantive. |
| `verification` | `edge_cases` | `edge_cases_count` / `acceptance_criteria_count` | integer | Counts from step 4. | Low counts relative to feature complexity indicate under-coverage of edge behavior. |
| `verification` | `edge_cases` | `criteria_have_concrete_inputs` | boolean | Whether acceptance criteria used concrete inputs and outcomes rather than vague statements. | Directly measures the Boundary rule that requirements must be testable. |
| `run.finished` | `finish` | `open_questions_count` / `out_of_scope_count` | integer | Counts from the required Output sections. | A chronically empty `out_of_scope_count` on ambiguous features is suspicious; rising `open_questions_count` signals recurring input gaps. |
| `run.finished` | `finish` | `unresolved_policy_flagged` | boolean | Whether a missing policy was marked unresolved rather than guessed. | Directly measures compliance with step 5's "do not guess missing policy" rule. |

An improvement agent should watch the `states_covered` distribution for
missing values, the rate of `criteria_have_concrete_inputs == false`, and
whether `unresolved_policy_flagged` is ever false alongside a nonzero
`open_questions_count`, to decide whether the Workflow or Boundary sections
of `SKILL.md` need revision.
