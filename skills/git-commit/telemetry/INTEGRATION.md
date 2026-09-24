# Integration guide: git-commit

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
| Before step 1 | `run.started` | `task_category` (`explicit_request`/`workflow_required`) |
| After step 3 (stage only explicit files or hunks) | `decision` (`phase=stage`) | `worktree_state`, `excluded_paths`, `staged_file_count` |
| After step 4 (infer type and scope) | `decision` (`phase=classify`) | `type`, `scope_included`, `breaking_change`, `subject_length` |
| After step 5 (commit after required checks) | `verification` (`phase=commit`) | `required_checks_run`, `checks_passed`, `commit_created` |
| Before step 6 (report) | `run.finished` | `type`, `commit_hash_present`, `checks_run` |
| When a maintainer later overturns the message or type | `user.correction` | `original_type`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`classify` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11` — "Use only when creating a Git commit ... is explicitly requested" and step 5's workflow-required alternative — became `task_category`.
- `SKILL.md:36-48` — the Conventional Commits type table — became the `type` enum.
- `SKILL.md:50` — the `!`/`BREAKING CHANGE:` breaking-change convention — became `breaking_change`.
- `SKILL.md:59` — "Never stage `.env`, credentials, private keys, or unrelated user work" — became `excluded_paths`.
- `SKILL.md:61` — "under 72 characters" subject-length rule — became `subject_length`.
- `SKILL.md:63` — "Run the repository's required checks first" — became `required_checks_run`/`checks_passed`.
- `SKILL.md:64` — "report the commit hash, subject, scope, and checks run" — became `commit_hash_present`/`checks_run`.

### Execution candidates

- None: this skill runs plain `git` commands rather than bundled scripts; their results are captured through the `stage`/`commit` events above instead of per-command instrumentation.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
