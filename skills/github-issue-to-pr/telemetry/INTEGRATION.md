# Integration guide: github-issue-to-pr

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
this skill's actual Workflow Phases (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before Phase 1 | `run.started` | `task_category` (`single_issue`/`batched_issues`/`backlog_scan`) |
| After Phase 1 (resolve and inspect scope) | `decision` (`phase=scope`) | `issue_state`, `scope_type` |
| After Phase 2 (analyze & plan, gate 1) | `decision` (`phase=plan`) | `execution_order_length`, `batching_used`, `issues_skipped`, `gate1_plan_approved` |
| After Phase 3 (verify, gate 2, gate 3) | `verification` (`phase=execute`) | `checklist_items_passed`, `gate2_diff_approved`, `gate3_pr_approved`, `pr_created` |
| Before Phase 4 (state management) | `run.finished` | `scope_type`, `prs_created`, `issues_completed`, `gates_passed` |
| When a maintainer later overturns the plan or PR | `user.correction` | `original_status`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`plan`/`execute` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:23` — "Process multiple issues only when the user explicitly authorizes ... Maintain strict one-issue-per-PR discipline" — became the `task_category`/`scope_type` enum.
- `SKILL.md:42` — Phase 1's stop conditions (existing PR, closed, stale, conflicting) — became `issue_state`.
- `SKILL.md:30` — the batching restriction (shared files or atomic feature, no conflicts) — became `batching_used`.
- `SKILL.md:32` — "Human approval required at three gates: (1) Prioritization plan, (2) Post-implementation diff, (3) Pre-PR creation" — became `gate1_plan_approved`/`gate2_diff_approved`/`gate3_pr_approved`/`gates_passed`.
- `SKILL.md:54` — "STOP HERE and wait for human approval of the plan" — became `gate1_plan_approved`.
- `SKILL.md:76-84` — the Verification Checklist's seven items — became `checklist_items_passed`.
- `SKILL.md:65` — "Only after approval: push and create the PR ... stop if publishing capability or permission is unavailable" — became `pr_created`.

### Execution candidates

- None: this skill has no bundled scripts; it drives `gh`/git-worktree operations directly, captured through the `scope`/`plan`/`execute` events above instead of per-command instrumentation.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
