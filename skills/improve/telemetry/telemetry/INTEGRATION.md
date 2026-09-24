# Integration guide: improve

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

- `SKILL.md:4` — compatibility: Requires filesystem-readable project files; Git history is used only when available.
- `SKILL.md:18` — `advisor-plans/` when `plans/` already has another purpose. Scratch data
- `SKILL.md:25` — require rotation when exposure is plausible.
- `SKILL.md:26` — - If the user requests execution or external publication, stop and ask for a
- `SKILL.md:44` — verification commands. Stop rather than guessing when scope is unclear.
- `SKILL.md:63` — selection, plan the top 3–5 corrective findings after dependency adjustment.
- `SKILL.md:76` — Stop when repository scope, evidence, a required safe command, or an
- `SKILL.md:77` — architectural/product decision cannot be established. Stop when live code has
- `references/audit-playbook.md:18` — - Evidence first. A pattern becomes a finding only when a concrete path, symbol, and impact are established.
- `references/audit-playbook.md:50` — - dependency advisories only when reachable in runtime or distribution paths,
- `references/audit-playbook.md:71` — Map risk before counting lines:
- `references/audit-playbook.md:104` — - Major migrations only after estimating changed packages, compatibility risks, rollout order, and rollback.
- `references/audit-playbook.md:117` — - absent agent instructions only when agents materially work in the repository.
- `references/finding-contract.md:16` — When the host supports preloaded skills or custom subagents, preload only the audit guidance needed for that auditor. Do not assume subagents inherit the parent conversation or safety rules.
- `references/finding-contract.md:43` — "impact": "An authenticated user could receive an invoice belonging to another tenant when IDs are known or exposed.",

### Verification candidates

- `SKILL.md:67` — 8. Validate persisted plans and scan them for sensitive output:
- `references/audit-playbook.md:34` — - check-then-act concurrency and missing transactions,
- `references/audit-playbook.md:47` — - schema validation, mass assignment, upload constraints, archive extraction,
- `references/audit-playbook.md:73` — - critical paths with no regression coverage,
- `references/audit-playbook.md:75` — - tests that assert mocks, snapshots without semantic assertions, or order-dependent behavior,
- `references/audit-playbook.md:113` — - inconsistent formatting/typecheck/lint enforcement,
- `references/audit-playbook.md:142` — State the user value, evidence, trade-offs, coarse effort, and the cheapest validation step. Do not propose generic category features.
- `references/plan-spec.md:68` — - `exact/new-test.ts` (create)
- `references/plan-spec.md:86` — **Verify**: `<command>`
- `references/plan-spec.md:93` — **Verify**: `<command>`
- `references/plan-spec.md:96` — ## Test plan
- `references/plan-spec.md:98` — - Test file and cases: happy path, original regression, named boundaries.
- `references/plan-spec.md:99` — - Existing exemplar test to follow.
- `references/plan-spec.md:107` — | Typecheck/build | `<command>` | exit 0 | yes |
- `references/plan-spec.md:108` — | Full regression | `<command>` | all pass or documented bounded exception | yes |

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
