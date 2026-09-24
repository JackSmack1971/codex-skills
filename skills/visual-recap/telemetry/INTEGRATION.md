# Integration guide: visual-recap

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

- `SKILL.md:16` — shared abstractions before authoring.
- `SKILL.md:17` — - Always publish a structured plan: UI headline when relevant, outcome
- `SKILL.md:21` — - Read the live block catalog before writing blocks; use exact runtime tags and
- `SKILL.md:33` — self-review → validate/render → publish. Stop when a required diff, visual
- `SKILL.md:39` — [wireframe reference](../references/wireframe.md) before any wireframe.
- `references/entrypoint-guidance.md:11` — when relevant, short outcome narrative, schema/API blocks when changed,
- `references/entrypoint-guidance.md:14` — Use wireframes for rendered UI changes, with before/after when comparison helps,
- `references/entrypoint-guidance.md:15` — after-only for additive changes, and a sequence when the change is stateful or
- `references/entrypoint-guidance.md:17` — states, components, and paths. Read `references/wireframe.md` before authoring
- `references/entrypoint-guidance.md:18` — any wireframe and visually inspect rendered output when a browser is available.
- `references/entrypoint-guidance.md:22` — Read the live block catalog before authoring; exact tags, required `id` fields,
- `references/entrypoint-guidance.md:25` — before/after code, and `annotated-code` for genuinely new code. Ground every
- `references/entrypoint-guidance.md:44` — hosted Plan tool; run the local check and serve the local bridge. Otherwise
- `references/entrypoint-guidance.md:51` — If the Plan connector or block catalog is unavailable, stop and tell the user
- `references/entrypoint-guidance.md:56` — Stop when the connector/block catalog cannot be validated, a required diff or

### Verification candidates

- `SKILL.md:33` — self-review → validate/render → publish. Stop when a required diff, visual
- `SKILL.md:34` — fact, connector/schema check, or safe redaction is unavailable; never invent
- `references/entrypoint-guidance.md:44` — hosted Plan tool; run the local check and serve the local bridge. Otherwise
- `references/wireframe.md:60` — `check`, `chevronDown`, `chevronUp`, `chevronLeft`, `chevronRight`, `dots`/`more`,
- `tests/evaluation-cases.md:3` — 1. **Normal:** Given a diff with interacting files, produce a recap matching actual files and validation.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
