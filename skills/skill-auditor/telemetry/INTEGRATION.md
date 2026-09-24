# Integration guide: skill-auditor

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
this skill's actual Audit workflow steps (superseding the generic candidate
scan below, which is kept only as provenance for why these points were
chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (operating mode) |
| After step 2 (context-sufficiency gate) | `decision` (`phase=gate`) | `proceeded_without_questions`, `questions_asked_count`, `missing_grounding_source` |
| After step 4 (rule-and-evidence ledger) | `verification` (`phase=evidence`) | `verified_quote_count`, `verified_observation_count`, `reported_count`, `estimated_count`, `unknown_count` |
| After step 5 (analyze applicable audit lenses) | `decision` (`phase=findings`) | `h_findings`, `m_findings`, `l_findings`, `lenses_applied` |
| After step 8 (validate, fix, revalidate) | `verification` (`phase=validate`) | `checklist_failed_count`, `revalidated` |
| Before returning output | `run.finished` | `mode`, `h_findings`, `m_findings`, `l_findings`, `remediation_requested` |
| When a maintainer later overturns a finding or the audit | `user.correction` | `original_severity`, `correction`, `finding_id` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`decision` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:40-46` — the Operating modes list (`quick-trace`, `standard-audit`, `workflow-audit`, `self-audit`, `remediation-plan`) — became the `task_category` enum.
- `SKILL.md:74-89` — the context-sufficiency gate's proceed-without-questions conditions and one-batch question rule — became the `gate`-phase `decision` fields.
- `SKILL.md:113-120` — the `[VERIFIED: QUOTE]`/`[VERIFIED: OBSERVATION]`/`[REPORTED]`/`[ESTIMATED]`/`[UNKNOWN]` calibration tags — became the `evidence`-phase `verification` fields.
- `SKILL.md:132-143` — the applicable audit lenses list (discovery metadata through evaluation coverage) — became the `lenses_applied` enum.
- `SKILL.md:211-217` — the H/M/L severity definitions — became `h_findings`/`m_findings`/`l_findings`.
- `SKILL.md:189-207` — the step-8 validate-fix-revalidate checklist — became `checklist_failed_count`/`revalidated`.

### Execution candidates

- `scripts/inventory_skill.py` and `scripts/validate_skill_pack.py` remain uninstrumented directly; they are read-only inventory/validation helpers whose results feed the `evidence` and `validate` phase events above rather than being instrumented per-subprocess-call, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
