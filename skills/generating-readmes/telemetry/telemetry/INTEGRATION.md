# Integration guide: generating-readmes

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

- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:32` — - Run `git rev-parse --show-toplevel` when git is available.
- `SKILL.md:33` — - If not a git repo, use the current working directory as the root and say so in the final report.
- `SKILL.md:38` — - Read the generated inventory output before drafting.
- `SKILL.md:39` — - Directly inspect the most important source files named by the inventory before making claims.
- `SKILL.md:44` — - Use `references/hook-guidance.md` only when the user wants this README workflow enforced by Codex CLI hooks.
- `SKILL.md:48` — - If a command is a strong convention but not explicitly present, either omit it or mark it `[INFERRED]`.
- `SKILL.md:53` — - If `--audit-only` is present, do not edit files. Return current score, gaps, and exact proposed changes.
- `SKILL.md:54` — - If `--no-write` is present, output the complete proposed README content in the response.
- `SKILL.md:55` — - Otherwise create or update the output path using the generated README.
- `SKILL.md:57` — 6. Verify before completion.
- `SKILL.md:59` — - If the score is below 24, fix the README and rerun the quality check once.
- `SKILL.md:60` — - Run only safe, read-oriented validation commands unless the user explicitly requested command execution evidence.
- `SKILL.md:65` — - Do not execute install, build, test, deploy, database, network, package-publish, or migration commands unless the user explicitly asks for live verification.

### Verification candidates

- `SKILL.md:11` — - **Trigger and exclusion:** Use to create, improve, audit, or verify a repository README or maintainer guide; exclude changelog reconstruction, routing to changelog-updater.
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:57` — 6. Verify before completion.
- `SKILL.md:59` — - If the score is below 24, fix the README and rerun the quality check once.
- `SKILL.md:60` — - Run only safe, read-oriented validation commands unless the user explicitly requested command execution evidence.
- `SKILL.md:65` — - Do not execute install, build, test, deploy, database, network, package-publish, or migration commands unless the user explicitly asks for live verification.
- `SKILL.md:76` — - Quickstart with prerequisites, install, run, and verify steps using grounded commands.
- `references/readme-blueprint.md:27` — - [Final self-check](#final-self-check)
- `references/readme-blueprint.md:45` — | Test command | scripts, Makefile, CI, test config | State honestly if none found. |
- `references/readme-blueprint.md:46` — | Lint/typecheck | scripts, config files, CI | Separate lint and typecheck when possible. |
- `references/readme-blueprint.md:94` — - Verify
- `references/readme-blueprint.md:149` — - Include actual test, lint, typecheck, and build commands when present.
- `references/readme-blueprint.md:223` — ## Final self-check
- `references/readme-blueprint.md:225` — Before completing, verify:
- `references/readme-blueprint.md:229` — - They can verify it works or see that no verification exists.

### Execution candidates

- `references/hook-guidance.md:11` — - Network and deployment actions: package publishing, Docker push, git push, cloud deploy, database migration, remote curl scripts.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
