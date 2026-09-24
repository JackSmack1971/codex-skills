# Integration guide: plugin-creator

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Wired instrumentation

`SKILL.md`'s `## Telemetry` section wires the following semantic events into
this skill's actual Quick Start and Validation steps (superseding the
generic candidate scan below, which is kept only as provenance for why these
points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before Quick Start step 1 | `run.started` | `task_category` (scaffold flow) |
| After Quick Start step 1 (scaffold script) | `operation` (`phase=scaffold`) | `plugin_name_normalized`, `companion_folders_created`, `marketplace_flag_used` |
| After Quick Start step 3 (marketplace entry) | `decision` (`phase=marketplace`) | `marketplace_target`, `policy_fields_set`, `marketplace_created_new` |
| After Validation (run `validate_plugin.py`) | `verification` (`phase=validate`) | `validation_passed`, `todo_placeholders_found`, `retry_count`; preceding `retry` event if repaired |
| Before handing back the plugin | `run.finished` | `plugin_created`, `marketplace_updated`, `deeplinks_emitted` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:17-19` — plugin-name normalization rules — became `plugin_name_normalized`.
- `SKILL.md:57-65` — optional companion folders (`skills/`, `hooks/`, `scripts/`, `assets/`, `.mcp.json`, `.app.json`) — became the `companion_folders_created` enum.
- `SKILL.md:110-118` — personal-vs-repo/team marketplace rules and the `--marketplace-name` exception path — became the `marketplace_target` enum.
- `SKILL.md:126-133` — required `policy.installation`/`policy.authentication`/`category` fields on every generated entry — became `policy_fields_set`.
- `SKILL.md:191,235-244` — "Do not leave `[TODO: ...]` placeholders" and the `validate_plugin.py` gate — became `todo_placeholders_found` and the `validate`-phase `verification`/`retry` events.
- `SKILL.md:214-225` — required `View`/`Share` Codex app handoff links after a marketplace-backed create/update — became `deeplinks_emitted`.

### Execution candidates

- `scripts/create_basic_plugin.py` and `scripts/validate_plugin.py` remain uninstrumented directly; their outcomes are captured through the `scaffold`/`marketplace`/`validate` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle. `scripts/update_plugin_cachebuster.py` and `scripts/read_marketplace_name.py` are left uninstrumented as they support the existing-plugin-update path outside the primary scaffold flow.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
