# Telemetry schema for review-agent

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `2a21dc4b54b411ba5cbfbbb44c6bdbee99b05269a54694f2a97fbc86f940e647`

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
wired into `SKILL.md`'s Telemetry section. They measure this skill's core
job — a read-only, defect-first review distinct from pr-review's merge-gate
decision — not just that a review happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`uncommitted_changes`, `base_branch_diff`, `commit`, `custom_instructions`) | Which local review target form was used. | Lets an improvement agent check whether one target form (e.g. `base_branch_diff`) correlates with worse comparison-boundary resolution or missed findings. |
| `verification` | `inspect` | `comparison_boundary_resolved` | enum (`local_branch`, `upstream_branch`, `merge_base`, `not_resolved`) | How the base-branch comparison ref was resolved for a `base_branch_diff` review. | Confirms the merge-base resolution rule (upstream-first, falling back to local) is actually followed rather than diffing against the branch tip. |
| `verification` | `inspect` | `files_reviewed_count` | integer | Number of changed files actually inspected. | A low count relative to the diff's changed-file total suggests partial review. |
| `verification` | `confirm` | `findings_confirmed_count` / `findings_discarded_count` | integer | Findings that survived vs. were dropped after checking tests/call sites in step 4. | A `findings_discarded_count` that is always zero suggests the confirmation step is pro forma rather than substantive. |
| `decision` | `report` | `finding_count` | integer | Total findings in the rendered result. | The primary output-volume signal; tracked against `no_findings` to detect over- or under-flagging drift. |
| `decision` | `report` | `priorities_used` | array of enum (`P0`, `P1`, `P2`, `P3`) | Which severity tiers actually appear. | Reveals skew toward low-value `P3` nits vs. the release-blocking `P0`/`P1` tiers the skill is meant to surface. |
| `decision` | `report` | `finding_categories` | array of enum (`correctness`, `security`, `performance`, `maintainability`) | Which "flag an issue only when" categories fired. | Confirms findings actually match the skill's own qualifying-issue criteria rather than drifting into style nits. |
| `decision` | `report` | `no_findings` | boolean | Whether the review legitimately reported `No findings.` | Distinguishes a clean change from a skipped review; a rate near zero across many trivial diffs would be suspicious in the other direction. |
| `run.finished` | `finish` | `read_only_confirmed` | boolean | Whether the run made no file edits, commits, branch pushes, or comment posts. | Directly measures the skill's hard read-only boundary, which is what distinguishes it from pr-review. |
| `user.correction` | — | `original_priority`, `correction`, `finding_category` | string | A human later dismissing a finding, confirming it, or changing its priority. | The ground-truth signal for defect-finding calibration — without it, `finding_count`/`priorities_used` only show what the skill claimed, not whether it was right. |

An improvement agent should join `decision`/`report` events against later
`user.correction` events (same `run_id`) to compute an approximate
false-positive rate per `finding_categories` value, and watch `priorities_used`
for drift toward `P3`-heavy results that would suggest a stricter qualifying
filter is needed in `SKILL.md`.
