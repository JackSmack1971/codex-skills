---
name: test-driven-development
description: Use only for a requested feature, bug fix, refactor, or test change that explicitly needs a red-green-refactor TDD cycle gated by local results. For broader QA planning or execution without TDD, use testing-qa.
compatibility: Requires Python 3.11+ and the project's existing test runner.
---

# Test-Driven Development

## Minimum contract

- **Trigger and exclusion:** Use only when the request explicitly requires a red-green-refactor TDD cycle; exclude broader QA without TDD, routing to testing-qa.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Write one behavior test first, run it, and require a genuine failure (`FAIL_CORRECT`) before implementation. Then implement the smallest change, run the target and full suite (`ALL_PASS`), refactor only under green, and run the full suite again. A passing red test or a test-runner error stops the cycle.

Run the portable verifier from this directory:

```text
python scripts/run_tdd_cycle.py --test-path <path> --stage red|green|refactor
```

The helper detects the project's supported test runner (including pytest,
Vitest, and Jest) from the current project. It emits one JSON result and never
invokes a shell command through `eval`. Do not invent a test path or claim
completion without all three stage results.

