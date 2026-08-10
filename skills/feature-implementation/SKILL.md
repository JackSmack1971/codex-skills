---
name: feature-implementation
description: Implement specified product behavior as the smallest verified change in an existing codebase. Use after requirements are concrete when the request is not primarily a cross-layer slice plan, an explicit red-green-refactor TDD cycle, or QA-only verification; compose those narrower skills when requested.
compatibility: Requires a readable repository and its available local toolchain.
---

# Feature Implementation

Ship the smallest complete behavior that satisfies the specification, using
existing repository conventions and dependencies.

## Workflow

1. Read the specification and acceptance criteria; list missing decisions.
2. Inspect the relevant architecture, callers, data flow, and existing tests.
3. Choose one end-to-end slice and identify the fewest files it needs.
4. Implement behavior with input validation, error handling, and accessibility
   or security requirements required by the contract.
5. Add or update the smallest meaningful verification, then run focused tests,
   lint/type checks, and the relevant broader check if available.
6. Report changed files, verification results, and any deferred work.

## Boundary

Do not invent product scope, broad refactors, abstractions for one use, or new
dependencies without need. Stop and ask when requirements conflict or a safe
data migration is required but not specified.

Use `vertical-slice` when the request centers on one user action crossing UI,
service/API, persistence, and verification. Use `test-driven-development` for
an explicit red-green-refactor constraint and `testing-qa` for QA without TDD.
