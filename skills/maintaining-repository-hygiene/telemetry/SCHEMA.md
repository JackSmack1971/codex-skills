# Telemetry schema for maintaining-repository-hygiene

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `f90ae962dc4532a44d686e3bfebb5ed27184892648b73d60bdee2e4c288a7899`

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
job — evidence-backed audit coverage and safe, idempotent issue/maintenance
publication — not just that an audit ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`audit`, `audit_publish`, `maintenance`, `verify`) | Which of the four documented operating modes was used. | Lets an improvement agent compare finding and publication outcomes across the skill's distinct modes. |
| `verification` | `preflight` | `remote_mode` | enum (`auto`, `on`, `off`) | Resolved remote mode from Inputs and operating modes. | Confirms remote coverage decisions are grounded in the resolved mode rather than assumed. |
| `verification` | `preflight` | `gh_available` / `python_version_ok` | boolean | Whether `gh` and a supported Python were present at Step 1. | Separates "audit was cautious because tooling was missing" from "audit missed available coverage," per Non-negotiable rule 3 (no fabricated coverage). |
| `decision` | `semantic` | `supplemental_findings_added` | integer | Findings added by the Step 3 semantic snapshot alignment pass. | A persistent zero on a documentation-heavy repository suggests the bounded semantic pass is not substantively occurring. |
| `decision` | `semantic` | `semantic_mismatch_found` | boolean | Whether the semantic pass found a documented-vs-implementation contradiction. | Tracks the yield of the two-evidence-anchor semantic-review requirement. |
| `decision` | `issues` | `issue_count` / `destructive_flagged_count` | integer | Size and destructive-flag count of the generated issue plan. | Detects drift toward over- or under-splitting atomic issue steps (Non-negotiable rule 5). |
| `decision` | `issues` | `publish_mode` / `published` | enum / boolean | Whether the run stayed draft-only or published issues. | Confirms publication only happens when the request explicitly authorized it (Section 3 defaults). |
| `operation` | `maintenance` | `label_prune_candidates` / `worktree_prune_candidates` | integer | Candidate counts from the label/worktree prune plans. | Surfaces the scale of destructive-maintenance proposals separately from audit findings. |
| `operation` | `maintenance` | `digest_confirmed` / `applied` | boolean | Whether the destructive plan's digest was confirmed before applying. | Directly measures the "fail closed on deletion" / digest-confirmation gate (Non-negotiable rule 7). |
| `verification` | `verify` | `resolved_findings` / `remaining_findings` / `new_findings` | integer | Finding-ID deltas from the post-remediation Verification loop. | The primary signal for whether remediation actually closed the findings this skill raised. |
| `verification` | `verify` | `verification_commands_passed` | boolean | Whether every issue-specific verification command passed. | Directly measures "do not claim repository alignment from issue creation alone." |
| `run.finished` | `finish` | `mode` / `issue_count` / `published` | mixed | Run summary. | Cross-run aggregation surface for the fields above. |
| `run.finished` | `finish` | `unresolved_critical_high` | integer | Count of unresolved critical/high findings at completion. | The headline risk signal from the Output contract; a rising trend flags a repository (or the audit itself) not converging. |
| `run.finished` | `finish` | `coverage_degraded` | boolean | Whether any coverage was degraded/skipped (missing `gh`, PyYAML, permissions). | Separates genuine repository cleanliness from coverage gaps that only look clean. |
| `user.correction` | — | `correction`, `category` | string | A maintainer later closing a published issue as invalid, or a finding proven incorrect. | The ground-truth signal for finding precision — without it, `issue_count` and `unresolved_critical_high` only show volume, not correctness. |

An improvement agent should track `coverage_degraded` and `gh_available`
together to separate real cleanliness from blind spots, watch
`digest_confirmed`/`applied` for any destructive operation that proceeded
without confirmation, and join `decision`/`verification` events against
later `user.correction` events (same `run_id`) to compute an approximate
false-positive rate per finding category.
