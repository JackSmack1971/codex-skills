# Integration guide: context7-skill-wizard

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

- `SKILL.md:10` — documentation. Keep the generated package in the workspace and stop before
- `SKILL.md:11` — external publication unless the user explicitly requests it.
- `SKILL.md:15` — 1. Extract a concrete library, framework, or domain. If it is missing, ask for
- `SKILL.md:16` — one specific technology before continuing.
- `SKILL.md:22` — derived topics. Retry once with a broader topic when a query is empty and
- `SKILL.md:25` — plan and wait for approval before writing the generated skill.
- `SKILL.md:30` — before packaging. Use the repository's migrated `skill-creator` package
- `SKILL.md:31` — helper when a `.skill` archive is explicitly requested.
- `SKILL.md:42` — - If Context7 is unavailable, report the exact gap and stop; do not silently
- `references/skill-template.md:8` — `license`, `metadata`, and `allowed-tools` when the host documents them.
- `references/skill-template.md:11` — platform names out of the name unless they are essential to the technology.
- `references/wizard-phase-guide.md:34` — Use one to three topic queries per selected library. Broaden once when a
- `scripts/validate_generated_skill.py:12` — if not lines or lines[0].strip() != "---":
- `scripts/validate_generated_skill.py:15` — end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
- `scripts/validate_generated_skill.py:20` — if line.strip() and not line.startswith((" ", "\t")) and ":" in line:

### Verification candidates

- `SKILL.md:4` — compatibility: Requires Codex CLI, Context7 MCP tools, and Python 3.11+ for local validation.
- `SKILL.md:54` — Report selected libraries, topics fetched, generated files, validation output,
- `VERIFICATION.md:20` — | `codex exec --skip-git-repo-check --sandbox read-only --ephemeral --ignore-user-config ...` with explicit `$context7-skill-wizard` | PASS; skill discovered and used, no files modified |
- `scripts/validate_generated_skill.py:2` — """Validate a generated Open Agent skill using only the standard library."""
- `scripts/validate_generated_skill.py:26` — def validate(skill_dir):
- `scripts/validate_generated_skill.py:55` — failures = validate(sys.argv[1])
- `tests/evaluation-cases.md:9` — 4. Validate a generated fixture with `scripts/validate_generated_skill.py` and

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
