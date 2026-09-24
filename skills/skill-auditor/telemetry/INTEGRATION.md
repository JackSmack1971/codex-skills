# Integration guide: skill-auditor

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

- `SKILL.md:28` — [ASSUMPTION: Audits are read-only unless a later, explicit execution step is delegated to an editing capability.]
- `SKILL.md:33` — - Ask questions only when missing information could materially change the findings.
- `SKILL.md:36` — - Do not invent product requirements. Apply canonical Agent Skill rules only when their provenance is declared.
- `SKILL.md:70` — Stop and request the target only when no target can be identified. Do not guess from unrelated context. When several candidates are plausible, present the smallest candidate list and ask the user to choose.
- `SKILL.md:74` — Proceed without questions when all are true:
- `SKILL.md:87` — Do not ask for information already present in the request or files. If the user says to proceed with minimal context, continue and label defaults and unknowns explicitly.
- `SKILL.md:89` — Stop condition: no audit may proceed without a readable target. Missing original intent lowers confidence but does not block an architecture-only audit when defaults are authorized.
- `SKILL.md:125` — Use the lean checks in this file first. Load [the full audit rubric](../resources/audit-rubric.md) for `standard-audit`, `workflow-audit`, `self-audit`, or when severity is uncertain.
- `SKILL.md:126` — When judging skill quality, retention, compression, or comparative value, also
- `SKILL.md:157` — For `workflow-audit`, require an ordered workflow or reconstruct one from artifacts and mark it `[ESTIMATED]`. If ordering cannot be established, report the limitation instead of asserting breakage.
- `SKILL.md:161` — Load [the report template](../resources/report-template.md) before finalizing the audit.
- `SKILL.md:187` — Write “None verified in the inspected scope” when a section has no findings.
- `SKILL.md:191` — Before claiming completion, verify:
- `SKILL.md:207` — If any item fails, revise the report and repeat the checklist. Do not claim “audited,” “verified,” or “complete” until the validation pass succeeds.
- `SKILL.md:217` — Do not inflate severity because a recommendation is easy or desirable. When evidence supports several severities, choose the lower one and state the uncertainty.

### Verification candidates

- `README.md:5` — ## Validate
- `SKILL.md:63` — - [ ] 8. Validate, fix, and revalidate
- `SKILL.md:121` — For absence claims, name the searched scope. Example: “No validation loop found in `SKILL.md` or the three directly linked resources.” Do not fabricate a quote for missing content.
- `SKILL.md:137` — - workflow determinism and validate-fix loops;
- `SKILL.md:152` — producer -> output artifact/state -> transport/path -> consumer input -> validation -> failure behavior
- `SKILL.md:155` — Check names, formats, paths, ownership, ordering, idempotency, error propagation, information loss, duplicated authority, and contradictory defaults.
- `SKILL.md:172` — 8. Audit Confidence and Validation.
- `SKILL.md:189` — ### 8. Validate, fix, and revalidate
- `SKILL.md:191` — Before claiming completion, verify:
- `SKILL.md:207` — If any item fails, revise the report and repeat the checklist. Do not claim “audited,” “verified,” or “complete” until the validation pass succeeds.
- `SKILL.md:214` — - `M`: recurring reliability loss, ambiguous control flow, material integration friction, incomplete validation, or substantial token/context waste.
- `SKILL.md:246` — - weakening evidence tags, stop conditions, or validation requirements.
- `SKILL.md:248` — Also check whether this skill’s own instructions create unnecessary questioning, circular authority, or impossible evidence requirements.
- `SKILL.md:265` — - [Evaluation cases](../resources/evaluations.md) — regression tests for this auditor.
- `SKILL.md:284` — - the report passed the validate-fix-revalidate checklist;

### Execution candidates

- `scripts/inventory_skill.py:153` — output.write_text(rendered, encoding="utf-8")
- `scripts/validate_skill_pack.py:182` — output.write_text(rendered, encoding="utf-8")

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
