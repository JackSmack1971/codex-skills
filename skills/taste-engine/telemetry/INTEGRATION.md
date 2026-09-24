# Integration guide: taste-engine

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
this skill's actual behavior (superseding the generic candidate scan below,
which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before reading the profile | `run.started` | `task_category` (`advisory_suggestion`/`state_update`) |
| After validating opt-in/profile | `verification` (`phase=validate`) | `opt_in_confirmed`, `profile_provided`, `legacy_config_avoided` |
| After selecting signals | `decision` (`phase=select`) | `signal_categories`, `signals_selected_count` |
| Before returning output | `run.finished` | `output_mode`, `signal_categories`, `state_mutated` |
| When the user later rejects/changes the suggestion | `user.correction` | `original_output_mode`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:9` — opt-in-only aid, signal categories (fonts, colors, layout density, aesthetic direction) — became `signal_categories`, `opt_in_confirmed`, `profile_provided`.
- `SKILL.md:11` — never invent a profile / never write to a legacy runtime config file / preserve schema on an explicit approved-or-rejected update, otherwise return a proposed patch or token block — became `legacy_config_avoided`, `output_mode`, `state_mutated`, `task_category`.
- `SKILL.md:13` — keep the profile path, opt-in flag, and output artifact visible in the response — informed tracking `output_mode`/`state_mutated` through to `run.finished`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
