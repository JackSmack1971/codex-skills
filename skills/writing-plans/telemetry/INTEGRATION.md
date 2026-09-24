# Integration guide: writing-plans

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
this skill's actual drafting/validate/save sequence (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before extracting feature name/date | `run.started` | `task_category` (`plan`/`task_list`/`implementation_design`) |
| After drafting the plan content | `decision` (`phase=draft`) | `sections_included`, `scope_rejected` |
| After `scripts/plan_tools.py validate` | `verification` (`phase=validate`) | `validate_status`, `placeholder_hit_count`, `task_count`; preceding `retry` event if repaired |
| After `scripts/plan_tools.py save` | `verification` (`phase=save`) | `save_status`, `output_location` |
| Before returning output | `run.finished` | `task_count`, `placeholder_hit_count`, `output_location`, `save_status` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:21` — "plan, task list, implementation design" request types and the default `docs/superpowers/plans/` location — became `task_category`/`output_location`.
- `SKILL.md:23` — "state the goal, architecture, stack, exact files, test-first steps, commands, expected results, and commit boundary. Reject specs that combine unrelated subsystems" — became `sections_included`/`scope_rejected`.
- `SKILL.md:29-30` — `plan_tools.py validate` and "the validator reports placeholder hits and task count as JSON. Fix every placeholder hit before saving." — became `validate_status`, `placeholder_hit_count`, `task_count`, and the retry-on-repair guidance.
- `scripts/plan_tools.py:42` — the validator's own `{"task_count", "placeholder_hit_count", "status"}` JSON fields — reused verbatim as the `validate`-phase evidence fields.
- `scripts/plan_tools.py:26-34` — the `save` subcommand's `SAVED`/error outcome — became `save_status`.

### Execution candidates

- `scripts/plan_tools.py`'s `date`, `validate`, and `save` subcommands are folded into the `draft`/`validate`/`save` events above rather than instrumented as separate subprocess-call events, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
