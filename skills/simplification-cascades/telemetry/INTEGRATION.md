# Integration guide: simplification-cascades

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
| Before step 1 | `run.started` | `task_category` (explicit vs. default target path) |
| After step 3 (parse scanner JSON) | `operation` (`phase=scan`) | `cascade_score`, `duplicate_patterns_count`, `special_case_hotspots_count`, `config_bloat_files_count`, `signals_detected` |
| After steps 5-6 (abstraction + elimination count) | `decision` (`phase=abstract`) | `elimination_count`, `cascade_valid`, `fit_violated_threshold`, `signal_types_addressed` |
| After step 7 (`--verify` rerun) | `verification` (`phase=verify`) | `verified`, `cascade_score`, `post_cascade_score`, `score_improved` |
| Before returning output | `run.finished` | `cascade_valid`, `elimination_count`, `verified`, `score_improved` |
| When a maintainer later rejects the abstraction | `user.correction` | `original_elimination_count`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:15` — "Extract a target directory from the request. Use `.` when none is given." — became the `task_category` enum.
- `SKILL.md:20-21` — the scanner's JSON fields (`duplicate_patterns`, `special_case_hotspots`, `config_bloat_files`, `cascade_score`) — became the `scan`-phase `operation` fields.
- `SKILL.md:26-28` — "Everything here is a special case of [X]," the 20%-fit test, and "at least three" eliminations — became `elimination_count`, `cascade_valid`, `fit_violated_threshold`.
- `SKILL.md:29-31` — rerun with `--verify` and "do not claim success unless the latter is lower" — became the `verify`-phase `verification` event and `score_improved`.
- `SKILL.md:22` — the zero-score/empty-lists report — became the `no_cascade_detected` failure class.

### Execution candidates

- `scripts/scan_cascade_signals.py` remains uninstrumented directly; its JSON output is captured through the `scan`- and `verify`-phase events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
