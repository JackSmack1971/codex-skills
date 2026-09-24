# Integration guide: systematic-debugging

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
this skill's actual Diagnostic workflow steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (failure class) |
| After step 1 (establish failure and baseline) | `verification` (`phase=baseline`) | `reproducible`, `intermittent`, `baseline_captured` |
| After step 3 (test a falsifiable hypothesis) | `decision` (`phase=hypothesis`) | `hypothesis_confirmed`, `failed_attempts`, `scope_expansion_requested` |
| After step 4 (correct the cause) | `operation` (`phase=correct`) | `containment_used`, `regression_check_added`, `defense_in_depth_added`, `scope_expansion_flagged` |
| After step 5 (verify and stop) | `verification` (`phase=verify`) | `symptom_resolved`, `regression_check_passes`, `surrounding_checks_clean`, `completion_status` |
| Before returning output | `run.finished` | `completion_status`, `failed_attempts`, `containment_used` |
| When a maintainer later disputes the diagnosis or fix | `user.correction` | `original_completion_status`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the accuracy analysis (`completion_status` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description naming bug/test/build/regression/unexpected-behavior triggers — became the `task_category` enum.
- `SKILL.md:36-44` — reproduction, intermittency recording, and pre-change baseline capture — became the `baseline`-phase fields.
- `SKILL.md:66-69` — "After three unsuccessful correction attempts, stop patching... Ask before expanding scope" — became `failed_attempts` and `scope_expansion_requested`.
- `SKILL.md:25-29` — the Invariant and containment exception's "temporary mitigation" concept — became `containment_used`.
- `SKILL.md:74-81` — the smallest-durable-regression-check, unrelated-refactor, and defense-in-depth rules — became `regression_check_added`, `scope_expansion_flagged`, `defense_in_depth_added`.
- `SKILL.md:93-101` — the five explicit completion-criteria bullets under step 5 — became `symptom_resolved`, `regression_check_passes`, `surrounding_checks_clean`, and `completion_status`.

### Execution candidates

- `scripts/find_polluter.py` remains uninstrumented directly; when used for order-dependent test pollution it is folded into the `correct`-phase `operation` event above instead of being instrumented per-subprocess-call, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
