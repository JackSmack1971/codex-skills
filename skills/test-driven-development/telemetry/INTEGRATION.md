# Integration guide: test-driven-development

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

- `SKILL.md:11` — - **Trigger and exclusion:** Use only when the request explicitly requires a red-green-refactor TDD cycle; exclude broader QA without TDD, routing to testing-qa.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:21` — Write one behavior test first, run it, and require a genuine failure (`FAIL_CORRECT`) before implementation. Then implement the smallest change, run the target and full suite (`ALL_PASS`), refactor only under green, and run the full suite again. A passing red test or a test-runner error stops the cycle.
- `references/testing-anti-patterns.md:5` — - Do not add mocks when a small real collaborator is available; mock only external or nondeterministic boundaries.
- `scripts/run_tdd_cycle.py:11` — args = command + ([test_path] if test_path else [])
- `scripts/run_tdd_cycle.py:21` — if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists() or (root / "tox.ini").exists():
- `scripts/run_tdd_cycle.py:24` — if package.exists():
- `scripts/run_tdd_cycle.py:26` — if "vitest" in data:
- `scripts/run_tdd_cycle.py:28` — if "jest" in data:
- `scripts/run_tdd_cycle.py:30` — if '"test"' in data:
- `scripts/run_tdd_cycle.py:40` — if not Path(args.test_path).is_file():
- `scripts/run_tdd_cycle.py:44` — if command is None:
- `scripts/run_tdd_cycle.py:48` — full_code, full_output = (target_code, target_output) if args.stage == "red" else run(command)
- `scripts/run_tdd_cycle.py:49` — if args.stage == "red":

### Verification candidates

- `SKILL.md:2` — name: test-driven-development
- `SKILL.md:3` — description: "Use only for a requested feature, bug fix, refactor, or test change that explicitly needs a red-green-refactor TDD cycle gated by local results. For broader QA planning or execution without TDD, use testing-qa."
- `SKILL.md:4` — compatibility: Requires Python 3.11+ and the project's existing test runner.
- `SKILL.md:7` — # Test-Driven Development
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:21` — Write one behavior test first, run it, and require a genuine failure (`FAIL_CORRECT`) before implementation. Then implement the smallest change, run the target and full suite (`ALL_PASS`), refactor only under green, and run the full suite again. A passing red test or a test-runner error stops the cycle.
- `SKILL.md:26` — python scripts/run_tdd_cycle.py --test-path <path> --stage red|green|refactor
- `SKILL.md:29` — The helper detects the project's supported test runner (including pytest,
- `SKILL.md:31` — invokes a shell command through `eval`. Do not invent a test path or claim
- `VERIFICATION.md:5` — - This repository has no project test runner, so the expected local result is a bounded no-runner error.
- `references/testing-anti-patterns.md:3` — - Do not call a test green because it imported successfully; assert the behavior.
- `references/testing-anti-patterns.md:4` — - Do not make the red test fail from a typo, missing fixture, or unavailable dependency.
- `references/testing-anti-patterns.md:7` — - Do not hide a full-suite regression behind a focused test result.
- `scripts/run_tdd_cycle.py:13` — proc = subprocess.run(args, capture_output=True, text=True, check=False)
- `scripts/run_tdd_cycle.py:21` — if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists() or (root / "tox.ini").exists():

### Execution candidates

- `VERIFICATION.md:4` — - Target is cross-platform and uses `subprocess.run` with argument arrays.
- `scripts/run_tdd_cycle.py:6` — import subprocess
- `scripts/run_tdd_cycle.py:13` — proc = subprocess.run(args, capture_output=True, text=True, check=False)

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
