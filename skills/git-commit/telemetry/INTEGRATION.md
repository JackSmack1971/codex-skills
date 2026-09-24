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

## Static candidates from the target

These are inspection hints, not runtime facts.

### Decision candidates

- `SKILL.md:3` — description: "Create commits or Conventional Commit messages when explicitly requested; use git-workflow for broader operations and github-issue-to-pr for the lifecycle."
- `SKILL.md:11` — - **Trigger and exclusion:** Use only when creating a Git commit or commit message is explicitly requested; exclude general Git inspection or synchronization, routing to git-workflow.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:22` — Inspect the actual diff before choosing the message or staging files.
- `SKILL.md:50` — Use `!` after the type or scope, or a `BREAKING CHANGE:` footer, for breaking
- `SKILL.md:62` — 5. Commit only when the user explicitly requested it or the established
- `SKILL.md:64` — 6. After committing, report the commit hash, subject, scope, and checks run.
- `SKILL.md:74` — Do not use interactive or destructive Git operations implicitly. If the
- `SKILL.md:75` — repository state is ambiguous, stop and report it before staging or committing.

### Verification candidates

- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:44` — | `test` | Tests |

### Execution candidates

- `SKILL.md:7` — # Git Commit
- `SKILL.md:11` — - **Trigger and exclusion:** Use only when creating a Git commit or commit message is explicitly requested; exclude general Git inspection or synchronization, routing to git-workflow.
- `SKILL.md:21` — Create a focused, semantic Git commit using the Conventional Commits format.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
