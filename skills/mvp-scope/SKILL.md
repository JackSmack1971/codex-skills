---
name: mvp-scope
description: Use to turn a product idea or capability list into explicit must-have, later, and won't-build scope decisions before specification or architecture. Do not use to discover the problem or write detailed feature behavior; use product-discovery or product-spec.
compatibility: Requires a product problem, desired outcome, constraints, or feature list.
---

# MVP Scope

Choose the smallest product that proves the intended value loop. Every item
must support a user outcome or a necessary safety/operational constraint.

## Workflow

1. State the user, problem, desired outcome, and MVP success condition.
2. Map each proposed capability to that outcome and note dependencies.
3. Classify items as Must have, Should have, Later, or Explicitly won't build.
4. Remove speculative flexibility, premature scale, admin, multi-tenancy,
   extensibility, and infrastructure that the success condition does not need.
5. Record risks, unresolved decisions, and the smallest end-to-end slice.

## Output

Produce `MVP_SCOPE.md` containing the success condition, included scope,
deferred scope, won't-build list, dependencies, risks, and a definition of
done. State what evidence would justify promoting a deferred item.

## Boundary

Do not silently drop a requested safety, accessibility, compliance, or data-
loss requirement. Flag it as a constraint even when it is not user-visible.
