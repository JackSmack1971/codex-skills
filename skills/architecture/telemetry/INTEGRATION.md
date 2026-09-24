# Integration guide: architecture

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
this skill's actual Modes/Output/Quality bar sections (superseding the
generic candidate scan below, which is kept only as provenance for why these
points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before starting (Mode selected) | `run.started` | `task_category` (`adr`\|`evaluation`\|`component_design`) |
| After Output (ADR/evaluation drafted) | `decision` (`phase=decide`) | `status`, `options_considered_count`, `do_nothing_considered` |
| After Quality bar checks 1, 3, 4 | `verification` (`phase=quality_bar`) | `constraints_stated`, `invalidation_conditions_stated`, `facts_assumptions_separated` |
| Before returning output | `run.finished` | `task_category`, `status`, `options_considered_count`, `action_items_count` |
| When a decider later changes the ADR's `Status` | `user.correction` | `original_status`, `new_status`, `reason` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the status-survival analysis an improvement agent should run over these
fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:30-34` — the three Modes (create an ADR, evaluate a system, design a component) — became the `task_category` enum.
- `SKILL.md:43` — `**Status:** Proposed | Accepted | Deprecated | Superseded` in the ADR template — became the `status` field and the `user.correction` status-transition event.
- `SKILL.md:53-67` — Options Considered / Trade-off Analysis structure — became `options_considered_count`.
- `SKILL.md:77-79` — Action Items section — became `action_items_count`.
- `SKILL.md:88-92` — Quality bar items 1-4 (state constraints, name alternatives including doing nothing, explain fit and invalidation, separate facts/assumptions/recommendations) — became the `quality_bar`-phase `verification` fields and `do_nothing_considered`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
