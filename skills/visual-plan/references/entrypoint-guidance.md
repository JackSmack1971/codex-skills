# Visual plan guidance

This reference contains the detailed operating doctrine behind the thin
`SKILL.md` activation surface.

## Plan construction

Research the real repository before drafting: name actual files, symbols,
routes, schemas, data shapes, and reusable helpers. Decide hard-to-reverse
wire-format, identity, ownership, auth, and rollout choices first. Publish a
standalone Agent-Native Plan, never an inline chat plan, and keep the document
as the source of truth when scope changes.

Use a structured plan with a concrete first read, outcome narrative, diagrams,
annotated code, file maps, open questions, and UI/prototype review when useful.
Skip visual planning only for genuinely trivial, unambiguous work. For a
non-trivial plan, surface it as the approval gate before implementation and
name the files or areas it will touch. Planning itself is read-only.

## Workflow and review

1. Inspect repository evidence and existing actions/components/helpers.
2. Choose the visual surface: document-only for backend/architecture, UI-first
   for product screens, prototype-first for functional behavior, design-first
   for branded fidelity, or visual-intake for an explicit questionnaire.
3. Read the block catalog before writing structured content; tags and required
   fields are runtime data, not memorized vocabulary.
4. Build the plan with real file paths and grounded data. Put unresolved,
   high-leverage decisions in one bottom question form with a recommended
   default.
5. Self-review for factual grounding, readable hierarchy, visual coverage,
   accessibility, privacy, and an actionable handoff.

Use `references/wireframe.md`, `references/canvas.md`,
`references/document-quality.md`, and `references/exemplar.md` for their
respective detailed rules. UI plans need realistic states, correct placement,
and the right surface; use renderer-owned `--wf-*` tokens and inspect a
rendered result when a browser is available.

## Boundaries

Local-files mode is valid for private material: run the local plan check and
serve the local bridge, never invent a hosted URL. Hosted plans must use the
URL returned by the plan service; private plans remain org/login gated. Never
publish secrets, credentials, private URLs, or unredacted environment values.
Treat comments as anchored review input, resolve detached anchors explicitly,
and update the plan rather than silently changing course.

Stop and report when the plan connector/block catalog is unavailable and the
local fallback cannot validate, when a required visual or data fact cannot be
grounded, when authentication is unavailable, or when user approval is
required before implementation.
