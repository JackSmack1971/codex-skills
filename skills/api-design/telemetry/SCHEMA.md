# Telemetry schema for api-design

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `fe93a6157c7f5d98022aac823aa1678e91fe0406fea29c19c2d1e54a9c915fd9`

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
wired into `SKILL.md`'s Telemetry section. They measure whether this skill's
contract designs actually cover the workflow's own required shape, not just
that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`http`, `rpc`, `graphql`, `internal`) | Which transport family was designed. | Lets an improvement agent check whether one transport family systematically gets thinner contracts (fewer error codes, fewer concerns addressed). |
| `decision` | `contract` | `transport` | enum (`http`, `rpc`, `graphql`, `internal`) | Transport actually specified in step 2. | Confirms step 2 output matches the declared task category rather than drifting. |
| `decision` | `contract` | `error_codes_count` | integer | Number of stable error codes defined. | A persistently low or zero count on non-trivial operations suggests step 2's error-code requirement is being skipped. |
| `decision` | `contract` | `empty_states_covered` | boolean | Whether empty states were addressed per step 2. | Directly measures step 2 compliance; a low rate across runs flags a workflow gap. |
| `decision` | `concerns` | `concerns_addressed` | array of enum (`auth`, `authz`, `rate_limits`, `pagination`, `idempotency`, `consistency`, `timeouts`) | Which step-3 cross-cutting concerns were actually specified. | Reveals whether step 3 is applied selectively based on real relevance or is being skipped wholesale. |
| `verification` | `check` | `naming_consistent` | boolean | Whether step 4's naming check passed. | Tracks whether the self-check is substantive rather than pro forma. |
| `verification` | `check` | `compatibility_risk_found` | boolean | Whether step 4 caught a compatibility risk. | Same rationale; a persistent zero on evolving contracts is suspicious. |
| `verification` | `check` | `sensitive_data_exposure_found` | boolean | Whether step 4 caught sensitive-data exposure. | Directly measures the Boundary's core safety guarantee ("never expose ... data a caller is not authorized to see"). |
| `verification` | `check` | `observability_defined` | boolean | Whether step 4 confirmed observability was defined. | Tracks completeness of step 4's checklist. |
| `run.finished` | `finish` | `concerns_addressed_count` | integer | Count of cross-cutting concerns in the final contract. | Trend line for whether contracts are growing thinner or more complete over time. |
| `run.finished` | `finish` | `boundary_additions_avoided` | boolean | Whether the run avoided adding versioning/pagination/abstraction without a stated client or scale need. | Directly measures Boundary-section discipline; a falling rate signals scope creep in generated contracts. |
| `user.correction` | — | `original_decision`, `correction`, `concern_category` | string | A later reviewer or implementer changing a contract decision this run made. | The ground-truth signal for calibration — without it, `decision` fields only show what the skill produced, not whether it was sufficient. |

An improvement agent should track the distribution of `concerns_addressed`
and `error_codes_count` against `task_category`, and join `decision` events
against later `user.correction` events (same `run_id`) to see whether
certain concern categories (e.g. `idempotency`, `rate_limits`) are
systematically under-addressed and need explicit emphasis in the Workflow
section.
