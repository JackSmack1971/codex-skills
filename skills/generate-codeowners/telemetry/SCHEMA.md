# Telemetry schema for generate-codeowners

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `6ae11f55f8b5a7aa46284f9b0baf749595123e0fdf2dc78f024aa6b2c9d0962c`

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
wired into `SKILL.md`'s Telemetry section. They measure whether ownership
assignments follow the skill's own evidence-order and archetype rules, and
whether generated files actually pass validation before delivery.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`generate`, `audit`) | Which of the two accepted modes this run performed. | Lets an improvement agent compare failure/gap rates between generation and audit runs. |
| `verification` | `audit` | `parser_errors` / `dead_rules_found` / `unowned_paths_count` / `individual_owner_risks` | integer | Counts from step 7's required audit report. | A chronic zero across many audited repositories suggests the audit checks aren't actually inspecting the file. |
| `verification` | `audit` | `shadowing_detected` | boolean | Whether a later broad rule was found shadowing an earlier specific one. | Directly measures whether the audit is catching the ordering hazard the Procedure explicitly warns about. |
| `decision` | `design` | `archetype` | enum (`focused_library_or_sdk`, `modular_application`, `enterprise_monorepo`, `open_source_project`, `internal_platform_or_infra`, `small_or_mixed`) | Repository classification from step 8. | Lets an improvement agent see whether ownership-gap rates or corrections cluster around one archetype, pointing at a design-policy gap for that shape of repository. |
| `decision` | `design` | `owner_resolution_sources` | array of enum (`owner_map`, `existing_codeowners_teams`, `github_visible_teams`, `personal_repo_owner`) | Which of step 9's evidence-order sources actually supplied owners. | Reveals whether the skill is resolving owners the way it claims (map first, then existing teams, then GitHub teams, then personal fallback) or defaulting too quickly. |
| `decision` | `design` | `unowned_domains_blocked_generation` | boolean | Whether step 12's gap check stopped generation. | The key safety signal — confirms the skill actually refuses to write an under-owned file rather than filling gaps with guesses. |
| `decision` | `design` | `dual_team_paths` | integer | Count of paths given two owning teams. | A rising count may signal domain boundaries are unclear, per step 11's caution about dual ownership. |
| `verification` | `validate` | `exit_code` / `retry_count` | integer | `validate_codeowners.py` result and repair cycles after rendering. | A rising retry rate points at a specific, recurring rendering defect worth fixing upstream of validation. |
| `verification` | `validate` | `self_owned` / `diff_scope_expected_only` | boolean | Whether `.github/CODEOWNERS` protects itself and the working-tree diff touched only the expected file. | These are the exact two conditions the Completion contract requires before claiming success; false on either means the run should not claim success. |
| `run.finished` | `finish` | `unowned_paths_count` | integer | Final unowned-path count at completion. | Tracked over time to see whether coverage is improving or degrading across runs on the same repository. |
| `user.correction` | — | `original_assignment`, `correction`, `archetype` | string | A maintainer later reassigning an owner, adding an unrecommended blank-owner exception, or dismissing an audit finding. | The ground-truth signal for whether this run's ownership judgment held up in practice. |

An improvement agent should join `decision`/`design` events against later
`user.correction` events (same `run_id`) to compute how often each
`archetype` or `owner_resolution_sources` value gets overturned, and watch
`unowned_domains_blocked_generation` and `diff_scope_expected_only` for
drift that would indicate the Procedure's ordering or evidence rules need
revision.
