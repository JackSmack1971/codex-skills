# Integration guide: grill-me

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
this skill's actual (delegated) session shape (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before the interrogation starts | `run.started` | `task_category` (`plan` \| `design`) |
| After the questioning runs its course | `decision` (`phase=interrogate`) | `questions_asked`, `assumptions_challenged`, `constraints_exposed`, `alternatives_tested`, `answer_sources` |
| Before enacting the plan or design | `verification` (`phase=confirm`) | `materially_sharper`, `shared_understanding_confirmed` |
| Before returning to the user | `run.finished` | `questions_asked`, `materially_sharper`, `shared_understanding_confirmed` |
| When the user later rejects a recommendation or names a gap | `user.correction` | `correction`, `detail` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this alias's
sessions.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description: "Compatibility alias for grilling... for a new interactive plan or design stress-test, use grilling." — became the `plan`/`design` `task_category` enum.
- `SKILL.md:9-11` — "Challenge assumptions, expose missing constraints, test alternatives, and keep questioning until the plan or design is materially sharper." — became `assumptions_challenged`, `constraints_exposed`, `alternatives_tested`, and `materially_sharper`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
