# Integration guide: data-modeling

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
| Before step 1 | `run.started` | `task_category` (`design`\|`review`) |
| After step 2 (identifiers, constraints, deletion behavior) | `decision` (`phase=constrain`) | `entities_count`, `uniqueness_constraints_count`, `foreign_keys_count`, `soft_delete_used` |
| After step 3 (read/write patterns and indexes) | `decision` (`phase=index`) | `indexes_added_count`, `justified_by_access_pattern` |
| After step 4 (normalization/concurrency trade-offs) | `verification` (`phase=tradeoffs`) | `normalization_choice`, `concurrency_assumptions_stated`, `transaction_boundaries_defined` |
| Before returning output | `run.finished` | `entities_count`, `indexes_added_count`, `unresolved_domain_questions` |
| When a reviewer later changes a modeling decision | `user.correction` | `original_decision`, `correction`, `entity` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — the frontmatter description "Design or review durable data models" — became the `task_category` enum.
- `SKILL.md:27-28` — "Define identifiers, required/optional fields, uniqueness, foreign keys, validation constraints, timestamps, and deletion behavior" — became the `constrain`-phase `decision` fields.
- `SKILL.md:29` — "Identify read/write patterns and add only necessary indexes" — became `indexes_added_count`/`justified_by_access_pattern`.
- `SKILL.md:31-32` — "State normalization or denormalization trade-offs, transaction boundaries, and concurrency assumptions" — became the `tradeoffs`-phase `verification` fields.
- `SKILL.md:37-38` — the Output section's "Mark unknown domain rules as questions" — became `unresolved_domain_questions`.
- `SKILL.md:42-43` — the Boundary section (no vendor choice or hypothetical fields; never weaken integrity to simplify code) — became `justified_by_access_pattern` and the `user.correction` block.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
