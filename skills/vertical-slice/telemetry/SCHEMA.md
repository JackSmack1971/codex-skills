# Telemetry schema for vertical-slice

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `82f95827e03fc55d48ab3c8faa386fe5e48cd0eba20ecbf6607ebea9553fb56b`

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
calls wired into `SKILL.md`'s Telemetry section. They measure whether the
skill actually traces one user action end to end across layers, rather than
completing technical layers in isolation.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | `"plan_only"` \| `"implement"` | Whether the run only produced a slice map or actually shipped the slice. | Lets an improvement agent compare completion quality (e.g. `success_path_verified` rate) between planning and implementing runs. |
| `decision` | `trace` | `layers_touched` | array of enum (`interface`, `service`, `persistence`) | Which layers the traced path actually crossed. | A run that never touches `persistence` or `interface` may indicate the "smallest path" is being truncated rather than genuinely traced end to end. |
| `decision` | `trace` | `stubs_used` | boolean | Whether the slice used explicit stubs for out-of-path work. | Confirms the "keeping stubs explicit" instruction is followed rather than silently building unrelated layers. |
| `decision` | `scope` | `contracts_changed` | integer | Count of contracts/schema changes identified for the path. | Outlier-high counts on a "smallest path" slice suggest scope creep beyond what step 3 calls for. |
| `decision` | `scope` | `cross_cutting_escalated` | boolean | Whether a cross-cutting requirement was escalated instead of forced into the slice. | Directly measures whether the Boundary section's escalation rule is actually exercised. |
| `verification` | `verify` | `success_path_verified` / `failure_path_verified` | boolean | Whether step 5's two required checks were both performed. | A `failure_path_verified: false` majority means the "most important failure path" half of step 5 is being skipped. |
| `run.finished` | `finish` | `follow_up_slices_count` | integer | Count of explicit follow-up slices named in the output. | A chronically zero count on non-trivial work is suspicious — it may mean deferred scope is being hidden rather than named. |
| `run.finished` | `finish` | `repo_left_runnable` | boolean | Whether the repository was left runnable after implementing. | Only meaningful when `task_category` is `implement`; a false value there is a direct Output-section violation. |

An improvement agent should check whether `layers_touched` consistently
covers interface-through-persistence for `implement` runs, watch the rate of
`failure_path_verified: false`, and compare `cross_cutting_escalated` against
`contracts_changed` to see whether the skill is absorbing cross-cutting work
it should instead be escalating per its own Boundary section.
