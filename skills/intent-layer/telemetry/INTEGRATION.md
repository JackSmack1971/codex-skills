# Integration guide: intent-layer

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
| Before Workflow step 1 (detect state) | `run.started` | `task_category` (`initial_setup` \| `maintenance`) |
| After Workflow steps 1-2 (detect state, route) | `decision` (`phase=route`) | `detected_state`, `route` |
| After Workflow step 4 (decide root/child nodes) or the maintenance-mode question | `decision` (`phase=plan`) | `child_nodes_planned`, `signals_triggered`, `maintenance_choice` |
| After Workflow step 5 (execute and validate) | `verification` (`phase=validate`) | `one_root_confirmed`, `read_first_directive_present`, `max_node_tokens` |
| Before returning output | `run.finished` | `route`, `nodes_created`, `max_node_tokens`, `maintenance_choice` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:18-19` — Workflow step 1-2 "Detect state ... Route: none/partial → Initial setup ... complete → Maintenance" — became `detected_state` and `route`.
- `SKILL.md:11-13` — Core Principle "Only ONE root context file" — became `one_root_confirmed`.
- `SKILL.md:37` — Workflow step 5 "Validate: one root, READ-FIRST directive, <4k tokens per node" — became `read_first_directive_present`, `max_node_tokens`.
- `SKILL.md:39-44` — Workflow step 6 "Maintenance mode: Audit nodes | Find candidates | Both" — became the `maintenance_choice` enum.
- `SKILL.md:46-55` — "When to Create Child Nodes" signal table (`>20k tokens`, responsibility shift, hidden contracts/invariants, cross-cutting concern) — became the `signals_triggered` enum and `child_nodes_planned`.

### Execution candidates

- `scripts/intent_tools.py`'s `detect-state`, `analyze`, and `estimate` subcommands remain uninstrumented directly; their outputs are captured through the `route`/`plan`/`validate` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
