# Integration guide: visual-recap

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
this skill's actual Inventory → read block schema/wireframe guidance →
author → self-review → validate/render → publish workflow (superseding the
generic candidate scan below, which is kept only as provenance for why these
points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before "Inventory" | `run.started` | `task_category` (`pr`/`branch`/`commit`/`diff`) |
| After "Inventory" | `decision` (`phase=inventory`) | `change_surfaces`, `key_change_tabs_count` |
| After "author grounded recap" | `operation` (`phase=author`) | `block_types_used`, `wireframe_used`, `wireframe_variant` |
| After "self-review → validate/render" | `verification` (`phase=validate`) | `block_catalog_validated`, `secrets_redacted`, `tabs_within_budget` |
| Before "publish" | `run.finished` | `publish_mode`, `block_types_used`, `key_change_tabs_count` |
| When a routed-back annotation overturns the recap | `user.correction` | `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:9-10` — description's PR/branch/commit/diff scope — became `task_category`.
- `SKILL.md:15-16` — "Inventory meaningful UI states, routes, roles, files, schemas, APIs, and shared abstractions before authoring." — became `change_surfaces`.
- `SKILL.md:19-20` — wireframes for rendered UI changes, entry/interaction/destination/permission states — became `wireframe_used`/`wireframe_variant`.
- `SKILL.md:23-24` — "Build data-model, api-endpoint, file-tree, diff, and annotated-code blocks mechanically from the real diff." — became `block_types_used`.
- `SKILL.md:25-26` — "Keep key diffs focused, summarized, annotated, and grouped in horizontal tabs" plus `references/entrypoint-guidance.md`'s 3–8 tab / ~150 line budgets — became `key_change_tabs_count`/`tabs_within_budget`.
- `SKILL.md:27-28` — "Keep private recaps gated... redact secrets... route reviewer annotations back into the plan/code loop." — became `publish_mode`, `secrets_redacted`, and the `user.correction` block.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument (the plan-service tool calls it drives are external MCP tools, not local scripts).

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
