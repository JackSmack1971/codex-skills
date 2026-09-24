# Telemetry schema for mvp-scope

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `fd058dd041650d4ecceec3c89bef0310e43c9d881b808b517ef095d24c97bec5`

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
calls wired into `SKILL.md`'s Telemetry section. They measure whether this
skill actually reduces scope to a proven value loop, rather than just
producing a plausible-looking `MVP_SCOPE.md`.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`problem`, `desired_outcome`, `constraints`, `feature_list`) | Which input form the run started from. | Lets an improvement agent check whether one input form (e.g. a raw feature list) correlates with worse trimming discipline. |
| `decision` | `classify` | `must_have_count` / `should_have_count` / `later_count` / `wont_build_count` | integer | Size of each Workflow-step-3 classification bucket. | A chronically empty `later_count`/`wont_build_count` suggests the skill is not actually cutting scope, just relabeling the input list as must-have. |
| `decision` | `trim` | `trimmed_categories` | array of enum (`speculative_flexibility`, `premature_scale`, `admin`, `multi_tenancy`, `extensibility`, `infrastructure`) | Which Workflow-step-4 removal categories actually fired. | Directly measures whether the skill follows its own required trimming checklist; missing categories on complex inputs are concrete gaps. |
| `decision` | `trim` | `items_removed` | integer | Count of capabilities cut during trimming. | Tracks whether trimming is substantive or pro forma. |
| `decision` | `trim` | `safety_constraint_preserved` | boolean | Whether a safety/accessibility/compliance/data-loss requirement was kept as a flagged constraint while trimming. | Directly measures compliance with the skill's own Boundary rule; a run that trims and answers `false` (or omits this) is a Boundary violation. |
| `verification` | `finalize` | `risks_count` / `unresolved_decisions_count` | integer | Counts recorded in Workflow step 5. | Rising or chronically zero counts on complex inputs flag whether risk-surfacing is genuine. |
| `verification` | `finalize` | `end_to_end_slice_defined` | boolean | Whether the smallest end-to-end slice was actually named. | The MVP's core deliverable per the skill's opening paragraph; a false rate above zero means the output is incomplete. |
| `run.finished` | `finish` | `must_have_count` / `wont_build_count` | integer | Final bucket sizes at close. | Compared against the `classify`-phase counts, reveals whether later steps (trim, risk review) changed the scope decision. |
| `run.finished` | `finish` | `promotion_criteria_stated` | boolean | Whether the Output's required "what evidence would justify promoting a deferred item" was included. | A required Output element; a low rate signals the skill is truncating its own contract. |

An improvement agent should watch the ratio of `must_have_count` to
`later_count`/`wont_build_count` for drift toward "everything is must-have,"
the rate of `safety_constraint_preserved == false`, and the rate of missing
`promotion_criteria_stated` to decide whether the Workflow or Output sections
of `SKILL.md` need revision.
