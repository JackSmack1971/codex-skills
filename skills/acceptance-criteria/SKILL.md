---
name: acceptance-criteria
description: Turn ambiguous requirements into observable pass/fail acceptance criteria for features, issues, and user journeys. Use when implementation or testing needs a precise behavioral contract.
compatibility: Requires a requirement, issue, product specification, or user journey.
---

# Acceptance Criteria

## Minimum contract

- **Trigger and exclusion:** Use when requirements need observable pass/fail behavior; exclude implementation design and QA execution, routing those to product-spec or testing-qa.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Define behavior from the user's and system's observable perspective. Prefer a
small set of complete scenarios over a long checklist of vague statements.

## Workflow

1. Identify actor, preconditions, trigger, input, and expected outcome.
2. Cover the happy path, validation failures, boundary values, empty/loading/
   error states, permissions, retries, and recovery when applicable.
3. Express each criterion as a verifiable Given/When/Then scenario or an
   equivalent precise statement.
4. Check for contradictions, missing actors, and untestable language.

## Output

Return numbered criteria grouped by journey, followed by assumptions, out of
scope behavior, and unresolved questions. Include a compact trace from each
criterion to the requirement it proves.

## Boundary

Do not prescribe implementation, test framework, or UI styling unless the
requirement explicitly demands it.
