# Integration guide: read-the-damn-docs

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
this skill's actual Required Workflow steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (Docs-First Trigger category) |
| After step 2 (search the web for official docs) | `verification` (`phase=search`) | `docs_already_local`, `web_search_performed`, `source_domain` |
| After step 4 (extract the facts needed) | `decision` (`phase=extract`) | `facts_extracted_count`, `breaking_changes_found`, `version_verified` |
| After step 6 (verify with the smallest useful check) | `verification` (`phase=verify_check`) | `check_type`, `check_passed` |
| Before the final answer | `run.finished` | `docs_named_in_answer`, `docs_unavailable_disclosed` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:25-48` — Docs-First Triggers list (latest/official request, package add/upgrade, fast-moving API, auth/secrets/compliance, deprecation errors, local contract docs, irreversible choices) — became the `task_category` enum.
- `SKILL.md:52-67` — "What Counts As Docs" source hierarchy (official docs, local repo docs, package registry metadata, source/types) — became the `source_domain` enum.
- `SKILL.md:79-80` — "verify the latest version before writing imports, config, or install commands" — became `version_verified`.
- `SKILL.md:84` — step 4's "breaking changes" extraction — became `breaking_changes_found`.
- `SKILL.md:86-87` — step 6's smallest-useful-check list (typecheck, tests, build, CLI dry run, API schema validation, local reproduction) — became the `check_type` enum.
- `SKILL.md:88-89` — step 7's "name the docs or local files consulted" — became `docs_named_in_answer`.
- `SKILL.md:124-128` — "If Docs Are Unavailable" disclosure requirement — became `docs_unavailable_disclosed`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
