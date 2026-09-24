# Telemetry schema for plugin-creator

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `a99fff0cda2b25c6d0b7a70fdbebb1989499e5c54b11afc3824d049b5c99b437`

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
skill scaffolds a valid, correctly-targeted plugin, not just that a script
ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`basic_scaffold`, `with_marketplace`, `repo_team_marketplace`, `existing_plugin_update`) | Which Quick Start flow the request needed. | Lets an improvement agent see whether the less-common `repo_team_marketplace`/`existing_plugin_update` flows are handled as reliably as the default scaffold. |
| `operation` | `scaffold` | `plugin_name_normalized` | boolean | Whether the requested name required hyphen-case/lower-case normalization. | Confirms the naming-normalization rule is actually applied, not just documented. |
| `operation` | `scaffold` | `companion_folders_created` | array of enum (`skills`, `hooks`, `scripts`, `assets`, `mcp`, `apps`) | Which optional companion folders (`--with-*` flags) were generated. | Reveals which companion structures are commonly requested, informing which get more scaffold-quality attention. |
| `operation` | `scaffold` | `marketplace_flag_used` | boolean | Whether `--with-marketplace` was passed during scaffolding. | Separates plugin-only failures from marketplace-registration failures downstream. |
| `decision` | `marketplace` | `marketplace_target` | enum (`personal_default`, `custom_name`, `repo_team`, `none`) | Which marketplace destination was used. | Confirms the "personal marketplace by default, repo/team only when explicitly requested" rule is followed. |
| `decision` | `marketplace` | `policy_fields_set` | boolean | Whether `policy.installation`, `policy.authentication`, and `category` were all written. | Directly measures the "Required behavior" rule that these fields must always be written, even at defaults. |
| `decision` | `marketplace` | `marketplace_created_new` | boolean | Whether a new marketplace file was seeded vs. an existing one updated. | Distinguishes first-run seeding bugs from update-path bugs. |
| `verification` | `validate` | `validation_passed` | boolean | Whether `validate_plugin.py` passed. | The skill's own required gate before handing back a plugin; a low pass rate points at a scaffold defect class. |
| `verification` | `validate` | `todo_placeholders_found` | integer | Count of leftover `[TODO: ...]` placeholders caught. | Directly measures the "must not contain `[TODO: ...]` placeholders" rule. |
| `verification` | `validate` | `retry_count` | integer | Number of repair attempts before validation passed. | A rising retry rate flags a recurring, fixable scaffold defect rather than one-off noise. |
| `run.finished` | `finish` | `plugin_created` / `marketplace_updated` | boolean | Whether the plugin and, if requested, the marketplace entry were successfully produced. | Separates plugin-scaffold quality from marketplace-registration quality in the final outcome. |
| `run.finished` | `finish` | `deeplinks_emitted` | boolean | Whether the required `View`/`Share` Codex app handoff links were included when a marketplace entry changed. | Directly measures compliance with the "end the final response with a short Codex app handoff" rule. |

An improvement agent should watch the `validation_passed` rate and
`retry_count` distribution per `task_category`, and check whether
`deeplinks_emitted` is ever false when `marketplace_updated` is true, to
decide whether the Quick Start or Required behavior sections of `SKILL.md`
need revision.
