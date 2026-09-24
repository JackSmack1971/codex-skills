# Integration guide: using-git-worktrees

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
this skill's actual `scripts/worktree.py` subcommand sequence (superseding
the generic candidate scan below, which is kept only as provenance for why
these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before `detect` | `run.started` | `task_category` (`create_worktree`/`verify_only`/`cleanup`) |
| After `detect` and `verify-ignore` | `verification` (`phase=detect`) | `worktrees_dir_status`, `ignore_status` |
| After `path` and `create` | `decision` (`phase=create`) | `branch_collision`, `create_status` |
| After `setup` and `test` | `verification` (`phase=validate`) | `setup_status`, `test_status`, `baseline_failures` |
| Before returning output | `run.finished` | `worktree_created`, `branch_collision`, `test_status` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:21` — detect → verify ignore → construct path → create → setup → test workflow, stopping on missing repo, branch collision, setup failure, or test failure — became the four wired events and their `--failure-class` values.
- `scripts/worktree.py:26` — `detect`'s own `FOUND_BOTH`/`FOUND_DOTWORKTREES`/`FOUND_WORKTREES`/`NOT_FOUND` status values — became `worktrees_dir_status`.
- `scripts/worktree.py:39` — `verify-ignore`'s own `IGNORED`/`NOT_IGNORED` status values — became `ignore_status`.
- `scripts/worktree.py:44-48` — `create`'s branch-existence check and `CREATED`/`BRANCH_EXISTS`/`ERROR` status values — became `branch_collision`/`create_status`.
- `scripts/worktree.py:52-54` — `setup`'s `SETUP_COMPLETE` status and `test`'s `NO_TEST_RUNNER` status — became `setup_status`/`test_status`.
- `tests/evaluation-cases.md:5` — the cleanup boundary case — became the `cleanup` value in `task_category`.

### Execution candidates

- `scripts/worktree.py`'s six subcommands are folded into the four wired events above (grouped by real decision point — detect, create, validate) rather than emitting one telemetry event per subcommand call, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
