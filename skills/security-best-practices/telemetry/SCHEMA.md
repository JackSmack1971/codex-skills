# Telemetry schema for security-best-practices

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `370f3365b65b70eeb8cfae6d3fa85326b49bef513577210880a6041dc004255a`

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
skill's language/framework coverage and finding calibration are sound, not
just that a security pass happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`implementation_guidance`, `passive_detection`, `security_report`) | Which of the step-4 requested modes the run was invoked for. | Lets an improvement agent see whether one mode (e.g. `security_report`) has systematically weaker reference coverage or calibration than the others. |
| `verification` | `scope` | `languages_detected` | array of enum (`python`, `javascript`, `typescript`, `go`) | Which supported languages were identified in step 1. | Confirms the skill is only triggering within its stated supported-language scope. |
| `verification` | `scope` | `references_loaded_count` | integer | Number of `references/` files loaded in step 2. | A count of zero on a matched stack is a compliance failure of the "load every matching reference" rule. |
| `verification` | `scope` | `reference_coverage_complete` | boolean | Whether both frontend and backend references were loaded for a full-stack application. | Directly measures step 2's explicit full-stack coverage requirement. |
| `decision` | `analyze` | `mode` | enum (same as `task_category`) | The mode actually applied during analysis. | Detects mode drift, e.g. giving report-style findings when only implementation guidance was requested. |
| `decision` | `analyze` | `findings_count` | integer | Number of issues identified (detection/report modes). | Tracked over time to detect drift toward over- or under-flagging. |
| `decision` | `analyze` | `trust_boundaries_considered` | array of enum (`authentication`, `authorization`, `tenant_ownership`, `validation`, `injection`, `secrets`, `logging`, `cookies`, `csrf`, `cors`, `redirects`, `uploads`, `dependency_reachability`) | Which General-cautions trust-boundary categories were actually examined. | Directly measures whether the skill's own stated boundary checklist is being applied, or narrowing to a favorite subset. |
| `verification` | `report` | `findings_by_severity` | object of integers (`critical`, `major`, `minor`) | Severity breakdown of a written report. | Detects severity-inflation or -deflation drift in Report mode. |
| `verification` | `report` | `secrets_reported_location_only` | boolean | Whether a discovered secret was reported by type/location only, without exposing its value. | Directly measures compliance with the "Report secret type and location only" rule — a critical safety property. |
| `run.finished` | `finish` | `mode` / `findings_count` | enum / integer | Final mode and finding count at close. | Cross-checked against `analyze`-phase values to confirm consistency through to output. |
| `run.finished` | `finish` | `awaiting_approval` | boolean | Whether the run stopped for explicit approval before implementing fixes. | Directly measures the "wait for explicit approval before implementing fixes" rule after a report. |
| `user.correction` | — | `original_severity`, `correction`, `trust_boundary` | string | A human later dismissing a finding as a false positive or changing its severity. | The ground-truth signal for severity calibration — without it, `findings_by_severity` only shows what the skill claimed, not whether it was right. |

An improvement agent should join `analyze`/`report` events against later
`user.correction` events (same `run_id`) to compute an approximate
false-positive rate per `trust_boundary` value, and watch whether
`reference_coverage_complete` is ever false for a detected full-stack
application to decide whether the Workflow or Reference map sections of
`SKILL.md` need revision.
