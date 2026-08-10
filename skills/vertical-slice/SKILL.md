---
name: vertical-slice
description: Plan or implement one end-to-end user-visible slice across interface, API or service logic, persistence, and verification. Use when a user action must be traced across layers or work is splitting into disconnected frontend, backend, or schema layers; use feature-implementation for ordinary feature delivery.
compatibility: Requires a repository or system boundary map and a concrete user action.
---

# Vertical Slice

## Minimum contract

- **Trigger and exclusion:** Use when one user action must be traced across interface, service, persistence, and verification; exclude ordinary feature delivery, routing to feature-implementation.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Follow one user action through the real system path instead of completing
technical layers in isolation.

## Workflow

1. Name the user action and its observable success condition.
2. Trace the smallest path from entry point through domain logic and storage
   to the returned/rendered result.
3. Identify only the contracts and schema changes needed for that path.
4. Implement or plan the slice in dependency order, keeping stubs explicit.
5. Verify the success path and its most important failure path end to end.

## Output

Provide a slice map, changed boundaries, acceptance checks, and explicit
follow-up slices. If implementing, leave the repository in a runnable state.

## Boundary

Do not build whole schemas, APIs, or UI layers ahead of the user value they
serve. Escalate cross-cutting requirements that genuinely cannot fit one slice.

This skill owns the cross-layer slice map. Compose `feature-implementation` to
ship the slice, `test-driven-development` only when TDD is explicit, and
`testing-qa` for broader verification.
