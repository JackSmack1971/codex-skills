# Integration guide: grilling

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
this skill's actual interview bullets (superseding the generic candidate
scan below, which is kept only as provenance for why these points were
chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before the first question | `run.started` | `task_category` (`plan` \| `design`) |
| After the question loop concludes | `decision` (`phase=interrogate`) | `questions_asked`, `branches_resolved`, `questions_without_recommendation`, `answer_sources` |
| Before enacting the plan or design | `verification` (`phase=confirm`) | `shared_understanding_confirmed`, `plan_enacted` |
| Before returning to the user | `run.finished` | `questions_asked`, `branches_resolved`, `shared_understanding_confirmed` |
| When the user later rejects a recommendation or names a missed branch | `user.correction` | `correction`, `detail` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
sessions.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description: "Use for a new interactive plan or design stress-test..." — became the `plan`/`design` `task_category` enum.
- `SKILL.md:11` — "Ask exactly one question at a time and wait for the user's answer." — became `questions_asked`.
- `SKILL.md:12` — "Walk each design branch in dependency order, resolving decisions before dependent questions." — became `branches_resolved`.
- `SKILL.md:13` — "Give a recommended answer with every question." — became `questions_without_recommendation`.
- `SKILL.md:14` — "Explore the codebase when it can answer the question instead of asking the user." — became the `answer_sources` enum.
- `SKILL.md:15` — "Do not enact the plan until the user confirms that shared understanding has been reached." — became the `confirm`-phase `verification` fields.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
