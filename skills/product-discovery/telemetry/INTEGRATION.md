# Integration guide: product-discovery

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
| Before step 1 | `run.started` | `task_category` (which dimension was vague) |
| After step 3 (list evidence/assumptions separately) | `decision` (`phase=classify_evidence`) | `evidence_count`, `assumption_count`, `invented_facts_flagged` |
| After step 4 (rank assumptions) | `decision` (`phase=rank`) | `assumptions_ranked`, `riskiest_assumption_identified` |
| After step 5 (define validation experiments) | `verification` (`phase=experiments`) | `experiments_count`, `signals_defined`, `decision_rules_defined` |
| Before returning output | `run.finished` | `open_questions_count`, `evidence_count`, `assumption_count`, `output_format` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11` — trigger/exclusion line naming problem/target-user/desired-outcome vagueness — became the `task_category` enum.
- `SKILL.md:28` — step 3 "List evidence and assumptions separately; do not invent market facts" — became `evidence_count`, `assumption_count`, `invented_facts_flagged`.
- `SKILL.md:29` — step 4 "Rank assumptions by uncertainty multiplied by consequence" — became `assumptions_ranked`/`riskiest_assumption_identified`.
- `SKILL.md:30` — step 5 "smallest validation experiments, their signals, and decision rules" — became the `experiments`-phase fields.
- `SKILL.md:36` — Output's file-vs-inline branching — became `output_format`.
- `SKILL.md:13` — required "unresolved assumptions" in the Output — became `open_questions_count`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
