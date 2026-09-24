# Telemetry schema for efficient-frontier

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `5f88123a801195a360c5def93ad2b09765f5afd5752ffe7c7010988ce5418c5a`

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
wired into `SKILL.md`'s Telemetry section. They measure whether delegation
actually happened along the skill's own lines, and whether the frontier
model genuinely reviewed the returned work rather than forwarding it.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`research`, `coding`, `testing`, `debugging`, `mixed`) | Which Common Scenarios category the delegated work fell under. | Lets an improvement agent see whether one scenario type (e.g. `debugging`) is delegated less often than the skill recommends, or fails more often when delegated. |
| `decision` | `delegate` | `subagents_spawned` | integer | Number of parallel subagents spawned for this run. | A persistent value of 0-1 on token-heavy tasks suggests the skill is being invoked but not actually changing behavior. |
| `decision` | `delegate` | `delegated_domains` | array of enum (`research`, `coding`, `testing`, `debugging`) | Which Common Scenarios categories were actually delegated. | Reveals whether delegation follows the skill's own scenario guidance or is applied indiscriminately. |
| `decision` | `delegate` | `stop_conditions_specified` | boolean | Whether the handoff packet included Useful stop conditions. | Handoff packets missing stop conditions are the most likely source of runaway or low-quality subagent work. |
| `verification` | `review` | `cited_files_reopened` | boolean | Whether the frontier model reopened files cited in delegated output. | Directly checks the Review Loop's core requirement, distinguishing real review from rubber-stamping. |
| `verification` | `review` | `disagreements_resolved` | integer | Count of subagent disagreements resolved at the frontier layer. | A chronic zero on multi-agent runs may mean disagreements are being silently dropped rather than resolved. |
| `verification` | `review` | `high_risk_diffs_skimmed` | boolean | Whether high-risk diffs were skimmed before acceptance. | Validates the Review Loop is substantive on the runs that matter most. |
| `run.finished` | `finish` | `guardrail_violations` | integer | Count of Guardrails violated during the run (e.g. concurrent edits to the same file, unverified high-risk conclusions). | The primary drift signal — a rising count means the Guardrails section needs to be strengthened or the orchestration prompt needs tightening. |

An improvement agent should aggregate `delegated_domains` against
`guardrail_violations` and `disagreements_resolved` across runs to see
whether a specific scenario type (e.g. `coding`) systematically produces
more Guardrail violations, which would justify tightening that scenario's
guidance in `SKILL.md`.
