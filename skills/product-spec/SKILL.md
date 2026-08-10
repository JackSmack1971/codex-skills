---
name: product-spec
description: Use after product intent is sufficiently understood to write an implementable feature specification covering behavior, requirements, edge cases, permissions, analytics, and acceptance criteria. Do not use to clarify a vague problem or reduce scope; use product-discovery or mvp-scope.
compatibility: Requires product intent and available repository or domain context when the feature belongs to an existing system.
---

# Product Specification

## Minimum contract

- **Trigger and exclusion:** Use when product intent is understood enough to define implementable behavior; exclude vague problem discovery and scope reduction, routing to product-discovery or mvp-scope.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Write an observable contract for one feature. Resolve ambiguity explicitly and
keep implementation choices out unless they are a stated constraint.

## Workflow

1. State the user, problem, desired outcome, and primary journey.
2. Define functional requirements and observable states: loading, empty,
   success, failure, retry, and recovery.
3. Define relevant non-functional requirements, permissions, data handling,
   analytics events, and operational constraints.
4. Cover edge cases and acceptance criteria with concrete inputs and outcomes.
5. Record out of scope and open questions; do not guess missing policy.

## Output

Produce `PRODUCT_SPEC.md` with sections: User, Problem, Journey, Functional
Requirements, Non-Functional Requirements, States and Errors, Permissions,
Acceptance Criteria, Analytics, Out of Scope, and Open Questions.

## Boundary

Keep requirements testable and technology-neutral. If a requirement cannot be
verified, mark it unresolved rather than hiding it in prose.
