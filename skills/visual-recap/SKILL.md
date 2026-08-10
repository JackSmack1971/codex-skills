---
name: visual-recap
description: >-
  Turn a PR, branch, commit, or git diff into an interactive visual recap with
  diagrams, file maps, API/schema summaries, annotated diffs, and focused
  review notes.
---

# Visual Recap

Use `/visual-recap` for a non-trivial PR, branch, commit, or diff that needs a
reviewable Agent-Native Plan. Derive the recap from the complete work unit,
not from a summary alone.

## Required behavior

- Inventory meaningful UI states, routes, roles, files, schemas, APIs, and
  shared abstractions before authoring.
- Always publish a structured plan: UI headline when relevant, outcome
  narrative, changed-file tree, and focused key-change evidence.
- Use wireframes for rendered UI changes; use the correct surface and show
  entry, interaction, destination, and permission/error states as needed.
- Read the live block catalog before writing blocks; use exact runtime tags and
  required fields.
- Build `data-model`, `api-endpoint`, `file-tree`, `diff`, and `annotated-code`
  blocks mechanically from the real diff. Use valid single-value JSON examples.
- Keep key diffs focused, summarized, annotated, and grouped in horizontal
  tabs; omit only redundant boilerplate, not review-critical evidence.
- Keep private recaps gated, use returned absolute URLs, redact secrets, and
  route reviewer annotations back into the plan/code loop.

## Workflow and stop conditions

Inventory → read block schema and wireframe guidance → author grounded recap →
self-review → validate/render → publish. Stop when a required diff, visual
fact, connector/schema check, or safe redaction is unavailable; never invent
implementation details.

Detailed mapping, budgets, publication, safety, grounding, and review-loop
guidance: [entrypoint guidance](references/entrypoint-guidance.md). Read the
[wireframe reference](references/wireframe.md) before any wireframe.
