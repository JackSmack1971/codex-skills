# Integration guide: visual-plan

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Static candidates from the target

These are inspection hints, not runtime facts.

### Decision candidates

- `SKILL.md:9` — Use `/visual-plan` when a plan benefits from a reviewable structured artifact:
- `SKILL.md:11` — Start from an existing Codex/Markdown/pasted plan when one exists. Skip it for
- `SKILL.md:20` — - Read the live block catalog before authoring structured blocks.
- `SKILL.md:23` — defaults; request approval before implementation.
- `SKILL.md:24` — - Read the relevant reference before authoring wireframes, canvas, or document
- `SKILL.md:25` — content, and inspect rendered UI when a browser is available.
- `SKILL.md:32` — and hand off. Stop when required facts, connector/schema validation,
- `references/canvas.md:5` — in full before authoring or editing any canvas/artboard content; do not author
- `references/canvas.md:21` — wireframe HTML; board-level artboard `x`/`y` IS allowed when it creates clear
- `references/canvas.md:24` — **Lay out mixed canvases in lanes.** When a canvas contains broad browser /
- `references/canvas.md:31` — frames. Before handoff, inspect the top canvas at default zoom and move any
- `references/canvas.md:34` — **Canvas annotations are designer notes on the artboard.** When a top canvas is
- `references/canvas.md:57` — edits. If an agent is working from exported source files, use
- `references/canvas.md:68` — or surfaces can disappear. If a full replacement is truly unavoidable, read the
- `references/canvas.md:70` — payload, and verify the source/export immediately after the update.

### Verification candidates

- `SKILL.md:32` — and hand off. Stop when required facts, connector/schema validation,
- `references/canvas.md:70` — payload, and verify the source/export immediately after the update.
- `references/document-quality.md:5` — pre-handoff check. Read it in full before authoring the plan document; it is the
- `references/document-quality.md:61` — implementation phases, risks, and validation. For architecture/code reviews,
- `references/document-quality.md:157` — should go beyond typecheck/unit tests when the plan changes UI, local files,
- `references/document-quality.md:174` — **Before handoff, open the plan and check it.** Fix overlap, excessive
- `references/entrypoint-guidance.md:51` — Local-files mode is valid for private material: run the local plan check and
- `references/entrypoint-guidance.md:59` — local fallback cannot validate, when a required visual or data fact cannot be
- `references/exemplar.md:22` — and a validation step — none of it repeating the canvas. If the task also
- `references/wireframe.md:60` — `check`, `chevronDown`, `chevronUp`, `chevronLeft`, `chevronRight`, `dots`/`more`,

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
