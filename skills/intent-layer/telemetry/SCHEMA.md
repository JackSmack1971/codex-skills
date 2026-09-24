# Telemetry schema for intent-layer

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `47147721c53299842f9435bb59fc42b57f31f9c538141c5a4318bba9179a9660`

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
skill actually routes correctly on repository state and respects its own
node-creation and validation rules, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`initial_setup`, `maintenance`) | Which top-level Workflow branch the run took. | Lets an improvement agent compare outcomes between building new Intent Layer infrastructure and maintaining existing infrastructure. |
| `decision` | `route` | `detected_state` | enum (`none`, `partial`, `complete`) | The state `detect-state` returned. | Confirms the routing decision is grounded in the detector's output rather than assumed. |
| `decision` | `route` | `route` | enum (`initial_setup`, `maintenance`) | Which path was taken given the detected state. | Detects any mismatch between `detected_state` and the route actually followed (e.g. `complete` routed into initial setup). |
| `decision` | `plan` | `child_nodes_planned` | integer | Number of child `AGENTS.md` nodes planned for initial setup. | Outlier-zero counts on a large, multi-boundary repository suggest under-application of the "When to Create Child Nodes" table. |
| `decision` | `plan` | `signals_triggered` | array of enum (`token_threshold`, `responsibility_shift`, `hidden_contracts`, `cross_cutting_concern`) | Which of the skill's own "When to Create Child Nodes" signals justified each planned node. | Directly measures whether node creation follows the stated signal table instead of ad hoc judgment. |
| `decision` | `plan` | `maintenance_choice` | enum (`audit_nodes`, `find_candidates`, `both`) or null | Which maintenance-mode option the user chose, when `route=maintenance`. | Tracks which maintenance activity is actually requested most, to prioritize that path's guidance. |
| `verification` | `validate` | `one_root_confirmed` | boolean | Whether the "only ONE root context file" invariant held. | Directly measures the Core Principle this skill is built around. |
| `verification` | `validate` | `read_first_directive_present` | boolean | Whether the required READ-FIRST directive was present. | Directly measures step 5's validation checklist. |
| `verification` | `validate` | `max_node_tokens` | integer | The largest node's token count. | Directly measures the "<4k tokens per node" limit; values creeping toward or past 4000 flag nodes that need splitting. |
| `run.finished` | `finish` | `route` / `nodes_created` / `max_node_tokens` / `maintenance_choice` | mixed | Run summary. | Cross-run aggregation surface for the fields above. |

An improvement agent should watch `max_node_tokens` for drift toward the 4k
limit, cross-tabulate `signals_triggered` against `child_nodes_planned` to
see which signal most often drives node creation, and compare `route`
against `detected_state` to catch routing logic that diverges from
`detect-state`'s output.
