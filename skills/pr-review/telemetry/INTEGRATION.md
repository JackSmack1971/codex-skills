# Integration guide: pr-review

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
this skill's actual Procedure steps (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (input form) |
| After step 1 (collect PR context) | `verification` (`phase=collect`) | `diff_truncated`, `gh_available` |
| After step 4 (decide findings) | `decision` (`phase=decide`) | `decision`, `blocking_findings`, `non_blocking_findings`, `finding_categories`, `risk_areas_touched` |
| After step 6 (validate before final output) | `verification` (`phase=validate`) | `exit_code`, `retry_count`; preceding `retry` event if repaired |
| Before returning output | `run.finished` | `decision`, `blocking_findings`, `submitted`, `submission_outcome` |
| When a maintainer later overturns the call | `user.correction` | `original_decision`, `correction`, `finding_category` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`decision` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:42` — draft-only default gated on `--submit-review` — became `submitted`/`submission_outcome`.
- `SKILL.md:57-65` — Review-stance priority order — became the `finding_categories` enum.
- `SKILL.md:96-101` — "Escalate scrutiny" trigger list — became the `risk_areas_touched` enum.
- `SKILL.md:80` — diff-truncation note — became `diff_truncated`.
- `SKILL.md:104-111` — finding validity/severity classification — became `blocking_findings`/`non_blocking_findings`.
- `SKILL.md:118-121` — `REQUEST_CHANGES`/`COMMENT`/`APPROVE` decision rules — became the `decision` enum.
- `SKILL.md:123-130` — `validate_review.py` gate — became the `validate`-phase `verification`/`retry` events.
- `references/hook-guidance.md:13-18` — existing PostToolUse validation guidance — corroborates the `validate`-phase wiring; still an optional ambient hook, not activated by this change.

### Execution candidates

- `scripts/collect_pr_context.py`, `scripts/validate_review.py`, `scripts/post_review.py` remain uninstrumented directly; their outcomes are captured through the `collect`/`validate`/`finish` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
