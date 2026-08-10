---
name: data-modeling
description: Design or review a durable data model from product requirements, including entities, relationships, ownership, lifecycle, constraints, indexes, migrations, and concurrency assumptions. Use when a feature stores or changes persistent data.
compatibility: Requires domain requirements and repository/database context when available.
---

# Data Modeling

## Minimum contract

- **Trigger and exclusion:** Use when product behavior stores durable data and entities, constraints, or access paths must be designed; exclude migration execution, routing to database-migrations.
- **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- **Shared baseline:** Apply the Core quality contract in `docs/core-quality-contract.md` for inputs, failure/stop, security, evaluation, runtime claims, and references.

Model the facts the product must preserve, then add only constraints and access
paths justified by actual behavior.

## Workflow

1. Extract entities, value objects, ownership, relationships, and lifecycle states.
2. Define identifiers, required/optional fields, uniqueness, foreign keys,
   validation constraints, timestamps, and deletion behavior.
3. Identify read/write patterns and add only necessary indexes.
4. State normalization or denormalization trade-offs, transaction boundaries,
   and concurrency assumptions.
5. Describe migration, backfill, audit, retention, and recovery implications.

## Output

Produce `DATA_MODEL.md` with an entity/relationship summary, constraints,
access patterns, lifecycle, concurrency notes, and migration plan. Mark
unknown domain rules as questions.

## Boundary

Do not choose a database vendor or add fields for hypothetical future use
without a stated constraint. Never weaken integrity merely to simplify code.
