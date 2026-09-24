# Integration guide: skill-creator

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
| Before step 1 | `run.started` | `task_category` (new skill vs. improve vs. migration) |
| After step 4 (eval contract + corpus) | `decision` (`phase=eval_design`) | `corpus_size`, `repetition_count`, `case_types`, `corpus_reduced_and_justified` |
| After step 6 (G1-G5 metrics + Design Readiness) | `verification` (`phase=score`) | `design_readiness_score`, `gates_passed`, `g5_status`, `validated_performance_reported` |
| After step 8 (validate the package) | `verification` (`phase=validate`) | `metadata_valid`, `references_valid`, `python_syntax_valid`, `redaction_clean`, `source_runtime_fields_removed` |
| Before returning output | `run.finished` | `design_readiness_score`, `g5_status`, `validated_performance_reported`, `package_validated` |
| When a later evaluation disputes the score/gate claims | `user.correction` | `original_g5_status`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the scoring-integrity analysis (`g5_status` vs. `validated_performance_reported`,
joined against later `user.correction`) an improvement agent should run over
these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:19-21` — "For a migration, inventory every source file..." vs. fresh authoring vs. improving an existing skill — became the `task_category` enum.
- `SKILL.md:26-29` — "Build positive, negative, and neighboring routing cases plus representative task and failure cases," default corpus and repetition counts, and "record any justified reduction" — became the `eval_design`-phase fields.
- `SKILL.md:36-39` — G1-G5 gates, Design Readiness `/50`, and "Static or deterministic validation leaves G5 UNVALIDATED" — became the `score`-phase fields.
- `SKILL.md:43` — "Validate the package... Check metadata, relative references, Python syntax, redaction boundaries, and that no source-runtime fields or commands remain" — became the `validate`-phase fields.
- `SKILL.md:77-80` — "Never call a deterministic validator behavioral evidence... Report the corpus, repetitions, matched baseline, metrics, and remaining uncertainty" — became the `user.correction` block's scoring-integrity concept.
- `SKILL.md:88-92` — the Stop conditions list — became the failure-class guidance.

### Execution candidates

- `scripts/quick_validate.py`, `scripts/package_skill.py`, and `eval-viewer/generate_review.py` remain uninstrumented directly; their outcomes are captured through the `score`- and `validate`-phase events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
