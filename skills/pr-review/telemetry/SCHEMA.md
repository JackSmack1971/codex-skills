# Telemetry schema for pr-review

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `c4af32aa1e45f7d461ec48eaed81c463b5da00f69564e2a4a8683888314674da`

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
wired into `SKILL.md`'s Telemetry section. They measure this skill's core
job — calibrated merge-risk judgment — not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`pr_number`, `pr_url`, `branch_range`, `diff_file`, `base_head_flags`) | Which input form was reviewed. | Lets an improvement agent check whether one input form correlates with worse outcomes (e.g. diff-file reviews systematically missing CI/context evidence). |
| `verification` | `collect` | `diff_truncated` | boolean | Whether the collector truncated the diff. | High truncation rates mean the collector's bound, not the review logic, is the actual bottleneck to fix. |
| `verification` | `collect` | `gh_available` | boolean | Whether GitHub metadata/CI status was reachable. | Separates "review was cautious because evidence was missing" from "review missed available evidence." |
| `decision` | `decide` | `decision` | enum (`REQUEST_CHANGES`, `COMMENT`, `APPROVE`) | Final verdict. | The primary calibration signal — its distribution and, combined with `user.correction`, its accuracy. |
| `decision` | `decide` | `blocking_findings` / `non_blocking_findings` | integer | Finding counts by severity class. | Detects drift toward rubber-stamping (via Anti-patterns) or excessive nitpicking. |
| `decision` | `decide` | `finding_categories` | array of enum (`correctness`, `security`, `data_integrity`, `reliability`, `test_coverage`, `performance`, `maintainability`, `style`) | Which Review-stance priority classes fired. | Reveals whether findings actually follow the skill's own stated priority order, or skew toward low-value categories (e.g. mostly `style`). |
| `decision` | `decide` | `risk_areas_touched` | array of enum (`auth`, `payment_or_irreversible`, `migrations_or_jobs`, `dependencies_or_ci`, `generated_or_vendored`, `none`) | Which "escalate scrutiny" triggers applied. | Confirms escalation rules actually engage on the PRs they're meant for. |
| `verification` | `validate` | `exit_code`, `retry_count` | integer | `validate_review.py` result and repair attempts. | A rising retry rate points at a recurring, fixable defect class in review generation (e.g. missing evidence field) rather than one-off noise. |
| `run.finished` | `finish` | `submitted`, `submission_outcome` | boolean / enum (`success`, `failure`, `not_attempted`) | Whether `--submit-review` was used and its result. | Separates draft-quality issues from submission-path issues. |
| `user.correction` | — | `original_decision`, `correction`, `finding_category` | string | A human later overturning this run's verdict or dismissing a finding. | The ground-truth signal for calibration — without it, `decision` counts only show what the skill claimed, not whether it was right. |

An improvement agent should join `decision` events against later
`user.correction` events (same `run_id`) to compute an approximate
false-positive/false-negative rate per `finding_categories` value, and watch
`finding_categories` distribution for drift away from the Review-stance
priority order in `SKILL.md`.
