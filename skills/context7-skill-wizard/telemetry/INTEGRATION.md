# Integration guide: context7-skill-wizard

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
| Before step 1 | `run.started` | `task_category` (`single_library`\|`multi_library`) |
| After step 2 (resolve-library-id) | `decision` (`phase=resolve`) | `libraries_resolved_count`, `library_ambiguous` |
| After step 4 (query-docs with retry) | `verification` (`phase=query`) | `topics_queried_count`, `empty_query_retried`, `coverage_gaps_count` |
| After step 7 (`validate_generated_skill.py`) | `verification` (`phase=validate`) | `validation_passed`, `retry_count`, `body_lines_count`; preceding `retry` event if repaired |
| Before returning the Completion report | `run.finished` | `libraries_selected_count`, `topics_fetched_count`, `coverage_gaps_count`, `validation_passed` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:21` — "For each selected library, call Context7 `query-docs`" — became the `single_library`/`multi_library` `task_category` enum.
- `SKILL.md:16-17` — resolving a library and presenting matches with their IDs — became `libraries_resolved_count`/`library_ambiguous`.
- `SKILL.md:21-23` — "query-docs for one to three derived topics. Retry once with a broader topic when a query is empty and record remaining coverage gaps as UNKNOWN" — became `topics_queried_count`, `empty_query_retried`, and `coverage_gaps_count`.
- `SKILL.md:29-30` — `scripts/validate_generated_skill.py` gate before packaging — became the `validate`-phase `verification`/`retry` events.
- `SKILL.md:40-41` — the 500-non-empty-body-line and 1024-character description limits — became `body_lines_count`.
- `SKILL.md:54-56` — the Completion section's required report contents (libraries, topics, generated files, validation output, UNKNOWN gaps) — became the `run.finished` evidence fields.

### Execution candidates

- `scripts/validate_generated_skill.py` remains uninstrumented directly; its outcome is captured through the `validate`-phase `verification` event above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
