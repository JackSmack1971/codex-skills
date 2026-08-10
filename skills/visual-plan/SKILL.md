---
name: visual-plan
description: >-
  Turn ordinary text plans into rich interactive visual plans with diagrams,
  file maps, annotated code, open questions, and UI/prototype review when
  useful.
---

# Agent-Native Plans

Use `/visual-plan` when a plan benefits from a reviewable structured artifact:
UI, workflows, architecture, data flow, options, or risky multi-file work.
Start from an existing Codex/Markdown/pasted plan when one exists. Skip it for
trivial, unambiguous work.

## Required behavior

- Research real files and reusable patterns first; planning is read-only.
- Publish a standalone structured Agent-Native Plan, never an inline plan.
- Choose document-only, UI-first, prototype-first, design-first, or
  visual-intake mode from the task.
- Read the live block catalog before authoring structured blocks.
- Ground paths, symbols, data, diagrams, and examples in repository evidence.
- Surface hard-to-reverse decisions and unresolved questions with recommended
  defaults; request approval before implementation.
- Read the relevant reference before authoring wireframes, canvas, or document
  content, and inspect rendered UI when a browser is available.
- Keep private material local or org/login-gated; never expose secrets or guess
  hosted/local plan URLs.

## Workflow and stop conditions

Inspect → choose surface → load block schema → draft → self-review → publish
and hand off. Stop when required facts, connector/schema validation,
authentication, or approval is unavailable instead of inventing details.

Detailed workflow, tool guidance, privacy, comment anchors, visibility,
sharing, setup, and examples: [entrypoint guidance](references/entrypoint-guidance.md).
Read these authoritative references as needed: [wireframe](references/wireframe.md),
[canvas](references/canvas.md), [document quality](references/document-quality.md),
and [exemplar](references/exemplar.md).
