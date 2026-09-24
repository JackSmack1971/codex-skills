# Integration guide: brainstorming-ux-features

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

- `SKILL.md:9` — Generate evidence-backed UX feature ideas and, when requested, convert the strongest candidate into a deterministic implementation contract for downstream agents.
- `SKILL.md:27` — Default to the full workflow unless the user explicitly requests only ideas or only a specification.
- `SKILL.md:32` — - User goal, product area, or UX concern when supplied
- `SKILL.md:44` — - Select one feature unless the user explicitly requests ideas-only output.
- `SKILL.md:73` — Stop only when the artifact validates, or when a blocking unknown cannot be resolved from available evidence. In the latter case, emit no implementation-ready contract; report the evidence gap and the smallest question needed to unblock it.
- `SKILL.md:93` — Do not treat an assumption as evidence. Include exact repository paths when available. If no repository is accessible, proceed using user context and assumptions, but lower `evidence_confidence` scores and make implementation paths provisional.
- `SKILL.md:121` — Apply the minimum gates first. A candidate is ineligible if any answer is `false`:
- `SKILL.md:149` — When scores are within 3 points, prefer in order:
- `SKILL.md:156` — `scripts/score_candidates.py` only computes and sorts numeric totals; if the top candidates are within 3 points, do the tie-break review manually using the order above before selecting one.
- `SKILL.md:160` — Read `resources/ux-principles.md` before finalizing the selected feature.
- `SKILL.md:176` — Acceptance criteria MUST be testable Given/When/Then contracts. Avoid subjective terms such as "intuitive," "clean," "fast," or "user-friendly" unless paired with an observable threshold.
- `SKILL.md:202` — 3. If validation fails, fix every reported error and run it again.
- `SKILL.md:235` — - Minimize collection of personal or sensitive data; define retention and deletion behavior when data is added.
- `resources/evaluations.md:3` — Run these evaluations with a fresh Codex run. Test at least one economical, balanced, and high-reasoning model when available.
- `resources/evaluations.md:25` — - Repository evidence is inspected before ideas are finalized.

### Verification candidates

- `SKILL.md:20` — - [Validation loop](#6-validation-loop)
- `SKILL.md:39` — The JSON file is the canonical handoff artifact. It MUST validate against `resources/feature-brief.schema.json` and the semantic checks in `scripts/validate_feature_brief.py`.
- `SKILL.md:69` — - [ ] 9. Validate, fix, and revalidate
- `SKILL.md:70` — - [ ] 10. Report the selected feature, path, score, and validation status
- `SKILL.md:115` — - A duplication check against existing capabilities
- `SKILL.md:189` — Use dependency IDs to define execution order. Put only dependency-free work in parallel groups. Include stop conditions for contract conflicts, missing paths, failed migrations, security violations, inaccessible dependencies, and failing validation.
- `SKILL.md:193` — ## 6. Validation loop
- `SKILL.md:202` — 3. If validation fails, fix every reported error and run it again.
- `SKILL.md:204` — 5. Do not hand the artifact to implementation agents while validation fails.
- `SKILL.md:227` — Validation: PASS
- `SKILL.md:251` — - `scripts/validate_feature_brief.py` — schema, semantic, path, and graph validation
- `VERIFICATION.md:5` — - Windows smoke check: `python scripts/validate_feature_brief.py --help`.
- `resources/evaluations.md:3` — Run these evaluations with a fresh Codex run. Test at least one economical, balanced, and high-reasoning model when available.
- `resources/evaluations.md:10` — - [Quality regression checklist](#quality-regression-checklist)
- `resources/evaluations.md:46` — Fix the failing unit test in src/parser.test.ts.

### Execution candidates

- `resources/example.feature.json:239` — "guardrail": "Do not increase duplicate task creation or repeated save requests."
- `resources/example.feature.json:302` — "system_response": "The application resubmits the current draft once and shows progress without duplicating requests.",
- `resources/example.feature.json:694` — "Confirm a double activation cannot create duplicate save requests."
- `scripts/score_candidates.py:96` — args.input.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
- `scripts/validate_feature_brief.py:163` — visiting.remove(node)

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
