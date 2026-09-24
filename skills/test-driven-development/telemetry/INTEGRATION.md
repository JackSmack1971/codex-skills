# Integration guide: test-driven-development

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
this skill's actual red-green-refactor cycle (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before the red stage | `run.started` | `task_category` (`feature`/`bug_fix`/`refactor`/`test_change`) |
| After the red stage (`--stage red`) | `verification` (`phase=red`) | `stage_result`, `runner_detected`, `mocks_used` |
| After the green stage (`--stage green`) | `verification` (`phase=green`) | `stage_result`, `retry_count` |
| After the refactor stage (`--stage refactor`) | `verification` (`phase=refactor`) | `stage_result`, `refactor_performed` |
| Before returning output | `run.finished` | `stages_reached`, `final_stage_result` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description's feature/bug fix/refactor/test change scope — became `task_category`.
- `SKILL.md:21` — red/green/refactor cycle description and the `FAIL_CORRECT`/`ALL_PASS` terms — became the per-phase `stage_result` enums.
- `SKILL.md:26` — `--stage red|green|refactor` flag — became the three `verification` phases.
- `SKILL.md:29-31` — helper detects pytest/Vitest/Jest — became `runner_detected`.
- `references/testing-anti-patterns.md:5` — mock only external or nondeterministic boundaries — became `mocks_used`.
- `scripts/run_tdd_cycle.py:49-58` — the `stage_result` values (`FAIL_CORRECT`, `PASS_UNEXPECTED`, `ERROR`, `TARGET_FAIL`, `REGRESSION`, `ALL_PASS`) the helper itself emits — became the enum values used across every phase and `final_stage_result`.

### Execution candidates

- `scripts/run_tdd_cycle.py`'s own JSON `stage_result` output is captured directly by the per-phase `verification` events above rather than instrumented as a separate subprocess-call event, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
