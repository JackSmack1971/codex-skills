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

## Static candidates from the target

These are inspection hints, not runtime facts.

### Decision candidates

- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:14` — - **Inputs:** Require the exact local review target and applicable repository instructions; establish the merge base or other comparison boundary before judging changes.
- `SKILL.md:15` — - **Failure/stop:** Stop when the target or comparison boundary cannot be resolved, evidence is inaccessible, or review would require mutation.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:30` — 3. Identify concrete regressions introduced by the change. Continue through the whole diff after
- `SKILL.md:35` — directly against the branch tip. Resolve the comparison ref to the branch's upstream when that
- `SKILL.md:36` — upstream exists and is ahead of the local branch; otherwise use the local branch. Run
- `SKILL.md:37` — `git merge-base HEAD <comparison-ref>`, then inspect `git diff <merge-base-sha>`. If the local
- `SKILL.md:38` — branch cannot be resolved, try its configured upstream explicitly before reporting that the target
- `SKILL.md:41` — Flag an issue only when all of these are true:
- `SKILL.md:47` — - The author would probably fix it if they knew about it.
- `SKILL.md:68` — If there are no qualifying findings, say `No findings.` Do not invent a finding to fill the result.
- `SKILL.md:69` — After the findings, add a brief overall assessment and mention any material test gaps or residual

### Verification candidates

- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:32` — 4. Check the relevant tests and call sites to confirm that each finding is real and actionable.
- `SKILL.md:69` — After the findings, add a brief overall assessment and mention any material test gaps or residual
- `VERIFICATION.md:5` — - `codex exec --ephemeral --sandbox read-only --skip-git-repo-check --ignore-user-config --ignore-rules --json` reported `$review-agent` as not discoverable in this no-Git workspace; the collector still inventories the package. Discovery parity remains UNKNOWN for this environment.
- `tests/evaluation-cases.md:3` — 1. **Normal:** In a Git repository with a supplied diff, invoke the skill and assert findings are ordered by severity and cite changed files.
- `tests/evaluation-cases.md:4` — 2. **Negative:** In a workspace without Git, assert the skill reports the target as unavailable rather than inventing a diff.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
