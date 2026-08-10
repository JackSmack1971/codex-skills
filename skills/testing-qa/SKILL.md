---
name: testing-qa
description: Use to choose or run proportionate QA checks across unit, integration, end-to-end, browser, performance, security, or release quality for an existing change. Do not use when the requested workflow is specifically red-green-refactor TDD; use test-driven-development.
compatibility: Requires the project's existing test and QA tools; no runner or dependency is assumed.
---

# Testing and QA

## Minimum contract

- **Trigger and exclusion:** Use to choose or run proportionate QA for an existing change; exclude an explicitly required red-green-refactor cycle, routing to test-driven-development.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Use this workflow to choose the smallest test strategy that proves the requested behavior. Inspect the repository first, reuse its existing runner, and report unavailable tooling as UNKNOWN instead of installing a framework by default.

1. Define the risk and test pyramid: focused unit checks first, integration checks for boundaries, and E2E/browser checks only for critical user paths.
2. Run the project's documented test, lint, type-check, security, and build commands when they exist.
3. For browser work, use the in-app browser skill or the project's existing automation; do not assume Playwright, Jest, pytest, or coverage thresholds.
4. Record failures with the exact command and a short safe summary. Separate pre-existing failures from regressions.
5. Before completion, verify the acceptance criteria, error paths, security boundaries, accessibility basics, and changed documentation.

The related `test-driven-development`, `security-best-practices`, and `pr-review` skills may be invoked when their narrower scope is actually requested. Do not reference unavailable skills or use `@skill` launcher syntax.
