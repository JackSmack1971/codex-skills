# Telemetry schema for git-commit

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `9a4e32c5956ea78f4ccb678f0504f101fc0ffe052ee540b96c39674e8f76dd0e`

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
wired into `SKILL.md`'s Telemetry section. They measure whether the skill
staged only what it should have and produced a correctly classified
Conventional Commit, not just that a commit happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`explicit_request`, `workflow_required`) | Why this run was invoked, per the Trigger/exclusion and step 5 rule. | Lets an improvement agent separate direct commit requests from commits made as part of a larger established workflow. |
| `decision` | `stage` | `worktree_state` | enum (`clean`, `mixed`, `already_staged`) | Worktree condition step 2 determined before staging. | A skewed distribution toward `mixed` suggests the skill is frequently invoked on messy worktrees, which raises the risk of staging unrelated work. |
| `decision` | `stage` | `excluded_paths` | array of enum (`env`, `credentials`, `private_keys`, `unrelated_files`, `none`) | Which of step 3's forbidden categories were actually found and excluded. | Directly verifies the "never stage `.env`, credentials, private keys, or unrelated user work" rule is being enforced, not just stated. |
| `decision` | `stage` | `staged_file_count` | integer | Files staged for this commit. | Outlier-high counts suggest the commit isn't staying "focused" as the Purpose requires. |
| `decision` | `classify` | `type` | enum (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`) | Conventional Commit type chosen from the Format table. | The core classification signal — its distribution and, combined with `user.correction`, its accuracy. |
| `decision` | `classify` | `scope_included` / `breaking_change` | boolean | Whether an optional scope was used and whether a breaking-change marker was needed. | Tracks whether the skill is using the full format correctly rather than defaulting to a bare type. |
| `decision` | `classify` | `subject_length` | integer | Character length of the commit subject line. | Values over 72 flag a direct violation of the skill's own subject-length rule. |
| `verification` | `commit` | `required_checks_run` / `checks_passed` | boolean | Whether step 5's "run the repository's required checks first" happened and passed. | Separates "the skill verified and it failed" from "the skill never actually ran the checks it claims to run." |
| `verification` | `commit` | `commit_created` | boolean | Whether a commit object was actually produced. | Distinguishes a deliberate stop (ambiguous state, no explicit request) from a silent no-op. |
| `run.finished` | `finish` | `commit_hash_present` | boolean | Whether step 6's report included a real commit hash. | A `finish` claiming success with no hash present is a hook-integrity signal worth investigating. |
| `user.correction` | — | `original_type`, `correction` | string | A maintainer later rewording the message, recategorizing its type, or amending the commit. | The ground-truth signal for whether this run's type/scope classification was actually correct. |

An improvement agent should join `classify` events against later
`user.correction` events (same `run_id`) to compute how often each `type`
value gets rewritten, and watch `excluded_paths` for any run where a
forbidden category was staged instead of excluded.
