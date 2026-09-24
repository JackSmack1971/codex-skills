# Integration guide: review-agent

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
this skill's actual "Review the change"/"Write the result" steps
(superseding the generic candidate scan below, which is kept only as
provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (local review target form) |
| After step 2 (inspect the complete diff) | `verification` (`phase=inspect`) | `comparison_boundary_resolved`, `files_reviewed_count` |
| After step 4 (check tests/call sites) | `verification` (`phase=confirm`) | `findings_confirmed_count`, `findings_discarded_count` |
| After "Write the result" | `decision` (`phase=report`) | `finding_count`, `priorities_used`, `finding_categories`, `no_findings` |
| Before returning the result | `run.finished` | `finding_count`, `priorities_used`, `read_only_confirmed` |
| When a finding is later dismissed or reprioritized | `user.correction` | `original_priority`, `correction`, `finding_category` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`decision` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:21-23` — description's local target forms (uncommitted changes, base-branch diff, commit, custom instructions) — became the `task_category` enum.
- `SKILL.md:34-39` — merge-base/upstream comparison-boundary resolution rule — became `comparison_boundary_resolved`.
- `SKILL.md:32` — step 4 "Check the relevant tests and call sites to confirm that each finding is real and actionable" — became `findings_confirmed_count`/`findings_discarded_count`.
- `SKILL.md:41-47` — the five qualifying-issue conditions (correctness/security/performance/maintainability impact, discrete, introduced by the change, demonstrable, author would fix) — became `finding_categories` and corroborate `findings_discarded_count`.
- `SKILL.md:62-66` — P0-P3 priority definitions — became the `priorities_used` enum.
- `SKILL.md:68` — "If there are no qualifying findings, say `No findings.`" — became `no_findings`.
- `SKILL.md:21-23` — "Do not modify files, create commits, push branches, or post review comments, or delegate the review" — became `read_only_confirmed`.

### Execution candidates

- None detected statically; this skill has no bundled scripts to instrument.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
