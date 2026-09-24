# Telemetry schema for github-issue-to-pr

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `36a677ee7612d24d7f9c378ee185ea358c4a3fff7d69bc3070e4905c6783f5dc`

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

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether the skill
kept its one-issue-per-PR discipline, actually stopped at its three human
approval gates, and produced verified, linked pull requests.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`single_issue`, `batched_issues`, `backlog_scan`) | Which Core Rules scope this run operated under. | Lets an improvement agent see whether batched or backlog-wide runs have higher correction or failure rates than the single-issue default. |
| `decision` | `scope` | `issue_state` | enum (`open`, `has_existing_pr`, `closed`, `stale`, `conflicting`) | Phase 1's resolved issue state. | Confirms Phase 1's stop conditions (existing PR, closed, stale, conflicting) are being checked before a branch is created. |
| `decision` | `scope` | `scope_type` | enum (`single_issue`, `batched_issues`, `backlog_scan`) | Actual scope processed, cross-checked against `task_category`. | Detects scope creep — e.g. a run that started `single_issue` but silently expanded. |
| `decision` | `plan` | `execution_order_length` / `issues_skipped` | integer | Size of Phase 2's recommended execution order and skip list. | Tracks planning quality on multi-issue runs; a skip list with no rationale recorded elsewhere is a gap. |
| `decision` | `plan` | `batching_used` | boolean | Whether Phase 2 clustered issues into a batch. | Cross-checked against Core Rules' batching restriction (shared files or atomic feature, no conflicts). |
| `decision` | `plan` | `gate1_plan_approved` | boolean | Whether the required "STOP HERE and wait for human approval" gate was actually passed. | The first of three mandatory gates — a `false` here with execution continuing is a hard policy violation. |
| `verification` | `execute` | `checklist_items_passed` | integer (of 7) | Items passed from the Verification Checklist run before every commit. | Directly measures whether the pre-commit checklist is substantive rather than pro forma. |
| `verification` | `execute` | `gate2_diff_approved` / `gate3_pr_approved` | boolean | Whether the post-implementation diff gate and pre-PR-creation gate were passed. | Confirms the remaining two mandatory human approval gates were honored before pushing or creating a PR. |
| `verification` | `execute` | `pr_created` | boolean | Whether a PR was actually created after gate 3. | Separates "approved and shipped" from "approved but publishing failed or was unavailable." |
| `run.finished` | `finish` | `prs_created` / `issues_completed` | integer | Final counts for the run. | The primary throughput signal, read against `scope_type` to see if batching genuinely improves throughput without more corrections. |
| `run.finished` | `finish` | `gates_passed` | integer (of 3) | How many of the three mandatory gates were passed this run. | A value under 3 on a run that still produced a PR is a direct process violation to investigate. |
| `user.correction` | — | `original_status`, `correction` | string | A maintainer later rejecting a created PR, or reversing a batching/skip decision from the approved plan. | The ground-truth signal for whether this run's plan and implementation held up in review. |

An improvement agent should join `plan`/`execute` events against later
`user.correction` events (same `run_id`) to see whether `batching_used` or a
particular `issue_state` correlates with more rejected PRs or reversed
plans, and flag any run where `gates_passed` is under 3 while `pr_created`
is true.
