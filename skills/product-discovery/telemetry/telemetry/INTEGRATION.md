# Integration guide: product-discovery

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

- `SKILL.md:3` — description: "Use first when the product problem, target user, or desired outcome is still vague; produce an evidence-backed problem statement, assumptions, and validation plan. Do not use for fixed scope decisions or an implementable feature specification; use mvp-scope or product-spec."
- `SKILL.md:11` — - **Trigger and exclusion:** Use when the product problem, target user, or desired outcome is vague; exclude fixed-scope specification or implementation planning, routing to mvp-scope or product-spec.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:21` — Clarify the problem before proposing a solution. Separate facts, assumptions,
- `SKILL.md:36` — success/failure signals, and open questions. If the user asks for an inline
- `SKILL.md:42` — opinions alone. Stop when the problem and next evidence-gathering step are clear.

### Verification candidates

- `SKILL.md:3` — description: "Use first when the product problem, target user, or desired outcome is still vague; produce an evidence-backed problem statement, assumptions, and validation plan. Do not use for fixed scope decisions or an implementable feature specification; use mvp-scope or product-spec."
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:30` — 5. Define the smallest validation experiments, their signals, and decision rules.
- `SKILL.md:41` — Do not design a feature, choose an architecture, or claim validation from
- `tests/evaluation-cases.md:3` — 1. **Normal:** Given a vague product request, define target user, problem, evidence, assumptions, and validation plan.
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given conflicting research, preserve uncertainty and propose the smallest discriminating validation.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
