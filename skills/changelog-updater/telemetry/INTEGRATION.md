# Integration guide: changelog-updater

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
| Before step 1 (establish context) | `run.started` | `task_category` (`reconstruct`\|`update_unreleased`\|`release`\|`render_only`) |
| After step 2 (collect history) | `operation` (`phase=collect`) | `commits_collected`, `collector_mode`, `merges_included` |
| After step 3 (build the semantic plan) | `decision` (`phase=plan`) | `sections_used`, `entries_count`, `omitted_commits_count`, `breaking_changes_flagged` |
| After step 4 (validate, preview, and apply) | `verification` (`phase=validate`) | `plan_valid`, `dry_run_reviewed`, `applied`, `allow_replace_used`; preceding `retry` event if repaired |
| After step 5 (verify) | `verification` (`phase=verify`) | `verify_exit_code`, `git_diff_check_passed` |
| Before returning output | `run.finished` | `mode`, `entries_count`, `omitted_count`, `backup_created` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:149-155` — the Mode selection table (`reconstruct`, `update_unreleased`/`release` via `since-tag`/`range`/`dates`, dry-run-only rendering) — became the `task_category` enum.
- `SKILL.md:163` — merge-commit default-exclusion rule — became `merges_included`.
- `SKILL.md:39,43` — Operating rules 5 and 9 (omit internal noise; omit or conservatively word ambiguous entries) — became `omitted_commits_count`.
- `SKILL.md:167-176` — the six Keep a Changelog sections and the `**Breaking:**` prefix rule — became `sections_used` and `breaking_changes_flagged`.
- `SKILL.md:40` — Operating rule 6 ("do not modify CHANGELOG.md until a plan validates and a dry run has been reviewed") — became `plan_valid`/`dry_run_reviewed`.
- `SKILL.md:122-130` — the `--allow-replace` destructive-reconstruction gate — became `allow_replace_used`.
- `SKILL.md:210-222` — the Completion gate checklist (`validate_plan.py` exit 0, dry-run reviewed, `verify_changelog.py` exit 0, `git diff --check` exit 0) — became the `validate`/`verify` phase fields.
- `SKILL.md:132` — the atomic-replacement/`CHANGELOG.md.bak` backup behavior — became `backup_created`.

### Execution candidates

- `scripts/collect_history.py`, `scripts/validate_plan.py`, `scripts/apply_changelog.py`, and `scripts/verify_changelog.py` remain uninstrumented directly; their outcomes are captured through the `collect`/`plan`/`validate`/`verify` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
