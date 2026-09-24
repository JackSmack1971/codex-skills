# Integration guide: design-md-ideator

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

- `SKILL.md:18` — - Never invent claimed brand facts. Mark working assumptions in the decision ledger; resolve or clearly disclose them before final output.
- `SKILL.md:19` — - Produce the final artifact at `DESIGN.md` unless the user specifies another path.
- `SKILL.md:46` — Search local context before questioning the user. Prefer, in order:
- `SKILL.md:74` — If the user delegates decisions, choose coherent defaults and label them `recommended`, not `confirmed`.
- `SKILL.md:89` — - Prefer `#RRGGBB` unless wide-gamut color is materially useful.
- `SKILL.md:92` — - Prefer a 4px base with an 8px primary rhythm unless context suggests otherwise.
- `SKILL.md:112` — For components, prioritize actual product atoms. Unless irrelevant, address buttons, chips, lists, tooltips, checkboxes, radio buttons, and input fields. Specify layout conventions and interaction states in prose; put machine-usable assignments in frontmatter.
- `SKILL.md:118` — Before generation, present a compact ledger containing:
- `SKILL.md:126` — Stop questioning when every required field is either `confirmed` or an explicitly disclosed `recommended` default. Do not block generation merely because the user delegated choices.
- `SKILL.md:140` — - Never include placeholders, `[TODO]`, unresolved alternatives, or commentary in the final file unless the user explicitly requests a draft.
- `SKILL.md:156` — If validation fails:
- `SKILL.md:163` — Do not deliver a strict-profile artifact that fails validation. If the runtime cannot execute Python, perform the same checks manually and explicitly disclose that script validation was unavailable.
- `SKILL.md:172` — - disclosed assumptions, if any remain by user choice.
- `SKILL.md:176` — Stop and report rather than fabricate when:
- `SKILL.md:181` — - validation still fails after fixes because the requested content violates the schema.

### Verification candidates

- `SKILL.md:3` — description: "Create, refine, reconstruct, or validate a standalone DESIGN.md design-system source of truth."
- `SKILL.md:9` — Create a complete `DESIGN.md` through guided design decisions, then validate it deterministically.
- `SKILL.md:41` — - [ ] 7. Validate, fix, and revalidate
- `SKILL.md:97` — Check contrast implications while ideating. Do not claim WCAG conformance without calculable foreground/background pairs.
- `SKILL.md:142` — ### 7. Validate, fix, and revalidate
- `SKILL.md:156` — If validation fails:
- `SKILL.md:160` — 3. Run validation again.
- `SKILL.md:163` — Do not deliver a strict-profile artifact that fails validation. If the runtime cannot execute Python, perform the same checks manually and explicitly disclose that script validation was unavailable.
- `SKILL.md:171` — - validation command and status;
- `SKILL.md:181` — - validation still fails after fixes because the requested content violates the schema.
- `SKILL.md:183` — Otherwise, continue through generation and validation without unnecessary confirmation gates.
- `VERIFICATION.md:12` — - [x] Validator exit codes distinguish pass, validation failure, I/O/usage failure, and internal failure.
- `resources/output-contract.md:95` — Before validation, manually check:
- `resources/portability.md:19` — - Python 3 is required only for deterministic validation.
- `resources/portability.md:36` — Run validation from the skill directory or invoke the script by absolute path.

### Execution candidates

- `tests/test_validator.py:7` — import subprocess
- `tests/test_validator.py:17` — proc = subprocess.run(

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
