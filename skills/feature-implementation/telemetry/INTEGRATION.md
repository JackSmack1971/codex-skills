# Integration guide: feature-implementation

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
this skill's actual Workflow steps (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category="feature_implementation"` |
| After step 1 (read spec, list missing decisions) | `decision` (`phase=scope`) | `missing_decisions_count`, `scope_conflict_flagged` |
| After steps 3-4 (choose slice, implement) | `decision` (`phase=implement`) | `files_touched`, `layer`, `input_validation_added`, `error_handling_added`, `security_or_accessibility_addressed` |
| After step 5 (add/update verification, run checks) | `verification` (`phase=verify`) | `tests_added_or_updated`, `focused_tests_passed`, `lint_type_checks_passed` |
| Before step 6 (report) | `run.finished` | `files_changed`, `layer`, `deferred_work_items` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:26` — "list missing decisions" — became `missing_decisions_count`.
- `SKILL.md:27` — "Inspect the relevant architecture, callers, data flow" — became the `layer` enum.
- `SKILL.md:28` — "identify the fewest files it needs" — became `files_touched`/`files_changed`.
- `SKILL.md:29-30` — "input validation, error handling, and accessibility or security requirements" — became the three implement-phase boolean fields.
- `SKILL.md:31` — "run focused tests, lint/type checks, and the relevant broader check" — became the `verify`-phase fields.
- `SKILL.md:38` — "Stop and ask when requirements conflict" — became `scope_conflict_flagged`.

### Execution candidates

- None: this skill has no bundled scripts; its checks are the repository's own test/lint/type tooling, captured through the `verify`-phase event rather than per-command instrumentation.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
