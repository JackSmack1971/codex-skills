# Integration guide: brainstorming-ux-features

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
this skill's actual numbered workflow sections (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 (repository discovery) | `run.started` | `task_category` (`ideas_only`\|`specification_only`\|`full_workflow`) |
| After step 2 (candidate generation) | `decision` (`phase=generate`) | `candidate_count`, `opportunity_classes_covered`, `candidates_rejected_count` |
| After step 3 (scoring and selection) | `decision` (`phase=score`) | `min_gates_failed_count`, `top_score`, `tie_break_applied` |
| After step 6 (validation loop) | `verification` (`phase=validate`) | `validation_status`, `retry_count` |
| Before returning output | `run.finished` | `mode`, `selected_feature_score`, `validation_status`, `blocking_questions_count` |
| When a stakeholder later overturns the selection | `user.correction` | `original_selection`, `correction`, `work_item_id` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the selection-calibration analysis an improvement agent should run over
these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:43-53` — Mode outputs (ideas-only, specification-only, full workflow) — became the `task_category`/`mode` enum.
- `SKILL.md:97-106` — the eight UX opportunity classes in "2. Candidate generation" — became the `opportunity_classes_covered` enum.
- `SKILL.md:117` — candidate rejection criteria (cosmetic, duplicate, unmeasurable, invented demand, rewrite-only) — became `candidates_rejected_count`.
- `SKILL.md:121-127` — the minimum-gates checklist in "3. Scoring and selection" — became `min_gates_failed_count`.
- `SKILL.md:149-156` — the within-3-points manual tie-break order — became `tie_break_applied`.
- `SKILL.md:193-206` — the "6. Validation loop" strict-validation requirement — became `validation_status`/`retry_count`.
- `SKILL.md:227-229` — the required final response format including "Blocking questions: none | <count>" — became `blocking_questions_count`.

### Execution candidates

- `scripts/score_candidates.py` and `scripts/validate_feature_brief.py` remain uninstrumented directly; their outcomes are captured through the `score`/`validate` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
