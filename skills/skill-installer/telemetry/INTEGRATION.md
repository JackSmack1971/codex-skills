# Integration guide: skill-installer

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
this skill's actual install flow (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before running the first helper script | `run.started` | `task_category` (list/install x curated/experimental/external) |
| After resolving the source | `decision` (`phase=resolve_source`) | `source_type`, `skills_requested_count`, `auth_method` |
| After the destination-conflict check | `verification` (`phase=conflict_check`) | `conflicting_skill_count`, `aborted_for_conflict` |
| After the install attempt (direct download or git fallback) | `verification`/`retry` (`phase=install`) | `install_method_used`, `fallback_triggered` |
| Before telling the user the skill is available next turn | `run.finished` | `skills_installed_count`, `source_type`, `install_method_used`, `conflicts_encountered` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and what an improvement agent should aggregate across runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11-14` — "List skills... Install from the curated list... Install from another repo" — became the `task_category` enum and `source_type` field.
- `SKILL.md:44` — "Defaults to direct download for public GitHub repos." — became `install_method_used=direct_download`.
- `SKILL.md:45` — "If download fails with auth/permission errors, falls back to git sparse checkout." — became `fallback_triggered`.
- `SKILL.md:46` — "Aborts if the destination skill directory already exists." — became the `conflict_check` phase.
- `SKILL.md:48` — "Multiple `--path` values install multiple skills in one run" — became `skills_requested_count`/`skills_installed_count`.
- `SKILL.md:53-54` — curated listing fetched via the GitHub API, private repos via git credentials or `GITHUB_TOKEN`/`GH_TOKEN`, git fallback tries HTTPS then SSH — became `auth_method` and the `git_https`/`git_ssh` enum values.

### Execution candidates

- `scripts/list-skills.py` and `scripts/install-skill-from-github.py` remain uninstrumented directly; their network/subprocess outcomes are captured through the `resolve_source`/`conflict_check`/`install` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
