# Integration guide: product-spec

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

- `SKILL.md:3` — description: "Use after product intent is sufficiently understood to write an implementable feature specification covering behavior, requirements, edge cases, permissions, analytics, and acceptance criteria. Do not use to clarify a vague problem or reduce scope; use product-discovery or mvp-scope."
- `SKILL.md:4` — compatibility: Requires product intent and available repository or domain context when the feature belongs to an existing system.
- `SKILL.md:11` — - **Trigger and exclusion:** Use when product intent is understood enough to define implementable behavior; exclude vague problem discovery and scope reduction, routing to product-discovery or mvp-scope.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:22` — keep implementation choices out unless they are a stated constraint.
- `SKILL.md:42` — Keep requirements testable and technology-neutral. If a requirement cannot be

### Verification candidates

- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
