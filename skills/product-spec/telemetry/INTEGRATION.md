# Integration guide: product-spec

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
| Before step 1 | `run.started` | `task_category` (new feature vs. existing-system extension) |
| After step 2 (functional requirements/observable states) | `decision` (`phase=define_states`) | `functional_requirements_count`, `states_covered` |
| After step 3 (non-functional/permissions/analytics/operational) | `decision` (`phase=non_functional`) | `permissions_defined`, `analytics_events_count`, `operational_constraints_flagged` |
| After step 4 (edge cases and acceptance criteria) | `verification` (`phase=edge_cases`) | `edge_cases_count`, `acceptance_criteria_count`, `criteria_have_concrete_inputs` |
| Before returning output | `run.finished` | `open_questions_count`, `out_of_scope_count`, `unresolved_policy_flagged` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:4` — compatibility line on repository/domain context "when the feature belongs to an existing system" — became the `task_category` enum.
- `SKILL.md:27-28` — step 2's required observable states (loading, empty, success, failure, retry, recovery) — became the `states_covered` enum.
- `SKILL.md:29-30` — step 3's non-functional requirements, permissions, data handling, analytics events, operational constraints — became the `non_functional`-phase fields.
- `SKILL.md:31` — step 4's "edge cases and acceptance criteria with concrete inputs and outcomes" — became `edge_cases_count`/`acceptance_criteria_count`/`criteria_have_concrete_inputs`.
- `SKILL.md:32` — step 5's "Record out of scope and open questions; do not guess missing policy" — became `open_questions_count`, `out_of_scope_count`, `unresolved_policy_flagged`.
- `SKILL.md:36-38` — required Output sections (Functional/Non-Functional Requirements, States and Errors, Permissions, Acceptance Criteria, Analytics, Out of Scope, Open Questions) — corroborate the field set above.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
