# Telemetry schema for skill-installer

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `fcab18502b7b993b4afa61fd724a906bae4d38a8a5cc46e1a5e27a0d58ea946a`

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
job — resolving the right source and installing without silent conflicts or
lost fallbacks — not just that a script ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`list_curated`, `list_experimental`, `install_curated`, `install_experimental`, `install_external_repo`) | Which of the skill's documented tasks (list vs. install, curated vs. experimental vs. external) was requested. | Lets an improvement agent check whether one task type (e.g. external-repo installs) has a disproportionate failure or fallback rate. |
| `decision` | `resolve_source` | `source_type` | enum (`curated`, `experimental`, `external_repo`, `private_repo`) | Which source the install/list actually resolved to. | Confirms the skill is routing to the source the user asked for, and shows how often private/external repos are used versus the curated default. |
| `decision` | `resolve_source` | `skills_requested_count` | integer | Number of skills named in one install call. | Distinguishes single-skill from batch installs for failure-rate analysis. |
| `decision` | `resolve_source` | `auth_method` | enum (`none`, `github_token`, `git_credentials`) | Which auth path was used for a private or rate-limited source. | Surfaces whether `GITHUB_TOKEN`/`GH_TOKEN` or git credentials are actually reachable when needed, per the Notes section. |
| `verification` | `conflict_check` | `conflicting_skill_count` | integer | How many requested skills already had an existing destination directory. | Measures how often the "aborts if the destination already exists" rule (Behavior and Options) actually fires. |
| `verification` | `conflict_check` | `aborted_for_conflict` | boolean | Whether the run aborted rather than installing due to a conflict. | Distinguishes user-facing abort friction from a genuine install failure. |
| `verification` / `retry` | `install` | `install_method_used` | enum (`direct_download`, `git_https`, `git_ssh`) | Which install path actually succeeded. | Tracks reliance on the git fallback over the direct-download default, which may indicate the download path needs attention. |
| `verification` / `retry` | `install` | `fallback_triggered` | boolean | Whether direct download failed and the git sparse-checkout fallback (HTTPS then SSH) was used. | A rising rate signals the "Defaults to direct download" path is degrading and the fallback is doing most of the work. |
| `run.finished` | `finish` | `skills_installed_count`, `source_type`, `install_method_used`, `conflicts_encountered` | integer / enum | Final tally for the run. | Cross-run aggregation of install reliability without re-reading logs. |

An improvement agent should track the `fallback_triggered` rate by
`source_type`, the `aborted_for_conflict` rate, and whether
`install_method_used` skews toward the git fallback over time — each is a
concrete signal that the Behavior and Options section's stated defaults need
revision.
