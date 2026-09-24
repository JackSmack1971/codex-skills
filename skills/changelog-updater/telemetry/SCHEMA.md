# Telemetry schema for changelog-updater

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `ec4dcf6e591580ea96fd74545868e9ec9cc8d5d2f94a35abd42a10e24a675149`

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
skill's evidence-first synthesis and completion gate actually hold, not
just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`reconstruct`, `update_unreleased`, `release`, `render_only`) | Which Mode-selection action was requested. | Lets an improvement agent check whether one mode (e.g. `reconstruct`) systematically produces more validation failures or omissions. |
| `operation` | `collect` | `commits_collected` | integer | Commits returned by `collect_history.py`. | Establishes the evidence volume behind the plan; near-zero on a non-trivial range flags a collector or range-selection problem. |
| `operation` | `collect` | `collector_mode` | enum (`full`, `since-tag`, `range`, `dates`) | Collector mode actually used in step 2. | Confirms step 2's mode matches the Mode-selection table for the declared `task_category`. |
| `operation` | `collect` | `merges_included` | boolean | Whether merge commits were included per step 2's default-exclusion rule. | Verifies the default-exclusion behavior is respected unless a merge carries unique release intent. |
| `decision` | `plan` | `sections_used` | array of enum (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`) | Which Keep a Changelog sections the plan populated. | Reveals whether entries are being mapped into the required section taxonomy or dumped into a nonstandard category. |
| `decision` | `plan` | `entries_count` | integer | Number of synthesized entries in the plan. | Baseline for judging Operating rule 4 ("prefer one outcome-oriented entry" over many implementation-level ones) — trending high counts suggest under-consolidation. |
| `decision` | `plan` | `omitted_commits_count` | integer | Commits explicitly omitted with a reason. | Tracks whether internal-only noise is actually being filtered per Operating rule 5, versus included wholesale. |
| `decision` | `plan` | `breaking_changes_flagged` | integer | Entries prefixed `**Breaking:**` per the Semantic classification section. | A persistent zero on a range known to include breaking changes signals a classification miss with direct user impact. |
| `verification` | `validate` | `plan_valid` | boolean | `validate_plan.py` result. | The first completion-gate checkpoint; a chronically failing first pass points at a systemic plan-construction gap. |
| `verification` | `validate` | `dry_run_reviewed` | boolean | Whether the dry-run diff was reviewed before `--write`. | Directly checks Operating rule 6 ("do not modify CHANGELOG.md until ... a dry run has been reviewed"). |
| `verification` | `validate` | `applied` | boolean | Whether the plan was written (vs. dry-run only, e.g. `render_only` task category). | Separates preview-only runs from mutating runs when reading aggregate stats. |
| `verification` | `validate` | `allow_replace_used` | boolean | Whether the destructive `--allow-replace` gate was invoked. | Full reconstruction is explicitly gated; tracks how often the destructive path is actually taken. |
| `verification` | `verify` | `verify_exit_code` | integer | `verify_changelog.py` exit code from step 5. | The second completion-gate checkpoint required before claiming success. |
| `verification` | `verify` | `git_diff_check_passed` | boolean | `git diff --check -- CHANGELOG.md` result. | Directly required by the Completion gate's final checklist item. |
| `run.finished` | `finish` | `backup_created` | boolean | Whether `CHANGELOG.md.bak` was created on replacement. | Confirms the writer's atomic-replacement/backup guarantee held for mutating runs. |

An improvement agent should aggregate `entries_count` vs. `omitted_commits_count`
per `task_category`, and watch the rate of nonzero `retry_count` (recorded via
a preceding `retry` event) at the `validate` phase to decide whether the
Semantic classification or Completion gate sections of `SKILL.md` need
revision.
