# Integration guide: vertical-slice

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
| Before step 1 | `run.started` | `task_category` (`plan_only`/`implement`) |
| After step 2 (trace the smallest path) | `decision` (`phase=trace`) | `layers_touched`, `stubs_used` |
| After steps 3-4 (identify contracts, implement/plan in dependency order) | `decision` (`phase=scope`) | `contracts_changed`, `cross_cutting_escalated` |
| After step 5 (verify success and failure paths) | `verification` (`phase=verify`) | `success_path_verified`, `failure_path_verified` |
| Before returning output | `run.finished` | `layers_touched`, `follow_up_slices_count`, `repo_left_runnable` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:26` — step 1's user action and observable success condition — informed `task_category` framing.
- `SKILL.md:27-28` — step 2's entry-point-through-domain-logic-to-storage trace — became `layers_touched`.
- `SKILL.md:29` — step 3's contracts/schema identification — became `contracts_changed`.
- `SKILL.md:30` — step 4's "implement or plan in dependency order, keeping stubs explicit" — became `stubs_used` and the `plan_only`/`implement` split in `task_category`.
- `SKILL.md:31` — step 5's success-path and failure-path verification — became `success_path_verified`/`failure_path_verified`.
- `SKILL.md:40-41` — the Boundary section's "escalate cross-cutting requirements" rule — became `cross_cutting_escalated`.
- `SKILL.md:35-36` — the Output section's "explicit follow-up slices" and "leave the repository in a runnable state" — became `follow_up_slices_count`/`repo_left_runnable`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
