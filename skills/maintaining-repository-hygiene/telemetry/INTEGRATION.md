# Integration guide: maintaining-repository-hygiene

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
this skill's Default-workflow checklist and its named steps/sections
(superseding the generic candidate scan below, which is kept only as
provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before Default-workflow step 1 | `run.started` | `task_category` (operating mode) |
| After step 1 (Preflight) | `verification` (`phase=preflight`) | `remote_mode`, `gh_available`, `python_version_ok` |
| After step 5 (Perform evidence-backed semantic snapshot alignment) | `decision` (`phase=semantic`) | `supplemental_findings_added`, `semantic_mismatch_found` |
| After steps 6-7 (generate/validate/publish the issue plan) | `decision` (`phase=issues`) | `issue_count`, `destructive_flagged_count`, `publish_mode`, `published` |
| After steps 8-9 (label/worktree maintenance plans; digest confirmation), Maintenance mode only | `operation` (`phase=maintenance`) | `label_prune_candidates`, `worktree_prune_candidates`, `digest_confirmed`, `applied` |
| After step 10 (Verification loop) | `verification` (`phase=verify`) | `resolved_findings`, `remaining_findings`, `new_findings`, `verification_commands_passed` |
| Before returning the Output contract | `run.finished` | `mode`, `issue_count`, `published`, `unresolved_critical_high`, `coverage_degraded` |
| When a maintainer later disputes a published finding/issue | `user.correction` | `correction`, `category` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:87-92` — Section 3 "Modes" (`Audit`, `Audit + publish`, `Maintenance`, `Verify`) — became the `task_category`/`mode` enum.
- `SKILL.md:125-132` — Step 1 Preflight (`--remote auto`; stop conditions for missing Git worktree, Python <3.10, unauthenticated `gh`) — became `remote_mode`, `gh_available`, `python_version_ok`.
- `SKILL.md:151-157` — Step 3 "Perform semantic snapshot alignment" (two-evidence-anchor requirement) — became `supplemental_findings_added`, `semantic_mismatch_found`.
- `SKILL.md:180-201` — Steps 4-5 (`issues-validate`, `issues-publish`, digest display and confirmation) — became `issue_count`, `destructive_flagged_count`, `publish_mode`, `published`.
- `SKILL.md:308-358` — Sections 8-9 Label/Worktree pruning ("fail closed on deletion"; digest confirmation before applying) — became the `maintenance`-phase `operation` fields.
- `SKILL.md:362-383` — Section 10 Verification loop (re-audit; compare resolved/remaining/new finding IDs; issue-specific verification commands) — became `resolved_findings`, `remaining_findings`, `new_findings`, `verification_commands_passed`.
- `SKILL.md:385-397` — Section 11 Output contract (coverage completed/degraded/skipped; unresolved critical/high findings) — became `unresolved_critical_high`, `coverage_degraded`.

### Execution candidates

- `scripts/repository_hygiene.py`'s `audit`, `findings-merge`, `issues-plan`, `issues-validate`, `issues-publish`, `labels-plan`, `labels-apply`, `worktrees-plan`, `worktrees-apply`, and `verify` subcommands remain uninstrumented directly; their outcomes are captured through the `preflight`/`semantic`/`issues`/`maintenance`/`verify`/`finish` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
