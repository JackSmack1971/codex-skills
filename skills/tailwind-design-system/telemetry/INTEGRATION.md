# Integration guide: tailwind-design-system

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

- `SKILL.md:11` — Before giving version-sensitive setup or configuration guidance, establish the
- `SKILL.md:16` — 2. The package manager's dependency tree when repository files are insufficient.
- `SKILL.md:20` — If evidence is missing or conflicting, say that the version is unknown and stop
- `SKILL.md:21` — before recommending version-sensitive setup. Do not silently choose v3 or v4.
- `SKILL.md:31` — accessibility guidance below version-neutral unless a section is explicitly
- `SKILL.md:37` — ## Use this skill when
- `SKILL.md:46` — ## Do not use this skill when
- `SKILL.md:56` — - If detailed examples are required, open `resources/implementation-playbook.md`
- `SKILL.md:57` — after the version gate succeeds.
- `VERIFICATION.md:3` — - The skill requires Tailwind major-version evidence before version-sensitive
- `resources/implementation-playbook.md:9` — ## When to Use This Skill
- `resources/implementation-playbook.md:39` — Before using either setup section, establish the Tailwind major version from
- `resources/implementation-playbook.md:40` — `package.json` plus the lockfile or installed package metadata. If the version
- `resources/implementation-playbook.md:51` — metadata wins when evidence disagrees.
- `resources/implementation-playbook.md:69` — so do not add a legacy `content` array by default. If a v4 project still needs

### Verification candidates

- `SKILL.md:12` — project's Tailwind major version from repository evidence. Check, in order:
- `SKILL.md:54` — - Apply relevant best practices and validate outcomes.
- `VERIFICATION.md:15` — python -m unittest discover -s tests -v
- `resources/implementation-playbook.md:700` — - **Don't forget dark mode** - Test both themes
- `tests/evaluation-cases.md:19` — 4. **Preservation:** Across all three cases, verify that token hierarchy,

### Execution candidates

- `resources/implementation-playbook.md:608` — root.classList.remove('light', 'dark')

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
