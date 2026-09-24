# Integration guide: testing-qa

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
this skill's actual numbered Workflow steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (primary QA focus) |
| After step 1 (define risk and test pyramid) | `decision` (`phase=scope`) | `pyramid_layers`, `risk_level` |
| After steps 2-4 (run commands, browser work, record failures) | `verification` (`phase=execute`) | `commands_run`, `commands_unavailable`, `regressions_found`, `pre_existing_failures` |
| After step 5 (verify before completion) | `verification` (`phase=final_check`) | `acceptance_criteria_checked`, `error_paths_checked`, `security_boundaries_checked`, `accessibility_checked`, `docs_checked` |
| Before returning output | `run.finished` | `pyramid_layers`, `regressions_found`, `overall_status` |
| When a maintainer later overturns the verdict | `user.correction` | `original_status`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis an improvement agent should run over these
fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description's unit/integration/browser/performance/security/release-quality scope — became `task_category` and the `pyramid_layers`/`commands_run` enums.
- `SKILL.md:23` — step 1's risk/test-pyramid definition — became `pyramid_layers`, `risk_level`.
- `SKILL.md:24` — step 2's documented test/lint/type-check/security/build commands — became `commands_run`.
- `SKILL.md:21` — "report unavailable tooling as UNKNOWN instead of installing a framework by default" — became `commands_unavailable` and the `overall_status: unknown` option.
- `SKILL.md:26` — step 4's failure recording, separating pre-existing failures from regressions — became `regressions_found`/`pre_existing_failures`.
- `SKILL.md:27` — step 5's pre-completion verification checklist — became the `final_check` boolean fields.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
