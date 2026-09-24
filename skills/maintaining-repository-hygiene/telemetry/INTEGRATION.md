# Integration guide: maintaining-repository-hygiene

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

- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:51` — Do not implement arbitrary repository changes during the audit. Produce implementation issues unless the user separately requests remediation.
- `SKILL.md:55` — 1. **Evidence before assertion.** Prefer manifests, lockfiles, workspace files, CI, build configuration, Git, and authenticated GitHub state over file-extension guesses.
- `SKILL.md:56` — 2. **Read-only first.** Audit before planning; plan before writing; recheck before deletion.
- `SKILL.md:59` — 5. **One issue per implementation step.** Group findings only when they share the same change boundary, owner, rollback, and verification evidence.
- `SKILL.md:61` — 7. **Fail closed on deletion.** Never delete a label after an incomplete history scan. Never prune worktree metadata when a fresh dry run differs from the reviewed plan.
- `SKILL.md:63` — 9. **Do not execute project code during discovery.** Do not install dependencies, run arbitrary build scripts, or execute repository binaries unless the user expands scope.
- `SKILL.md:64` — 10. **Do not broaden scope silently.** Branch deletion, history rewriting, file removal, ruleset edits, and repository-setting changes remain issue-based recommendations unless explicitly requested through a separate reviewed workflow.
- `SKILL.md:66` — Read the complete decision rubric when interpreting findings: [references/audit-rubric.md](../references/audit-rubric.md).
- `SKILL.md:84` — - issue behavior: generate validated drafts; publish only when the request explicitly asks to create/open/publish issues;
- `SKILL.md:92` — - **Verify:** re-audit after implementation and compare stable finding IDs.
- `SKILL.md:106` — - [ ] 7. Publish issues when explicitly requested
- `SKILL.md:107` — - [ ] 8. Generate label/worktree maintenance plans when applicable
- `SKILL.md:108` — - [ ] 9. Review and confirm destructive-plan digests before applying

### Verification candidates

- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:90` — - **Audit + publish:** report, validate, then create every planned issue.
- `SKILL.md:92` — - **Verify:** re-audit after implementation and compare stable finding IDs.
- `SKILL.md:105` — - [ ] 6. Generate and validate the authoritative atomic issue plan
- `SKILL.md:149` — Read `report.md`, then inspect the JSON evidence for every critical/high finding and every low-confidence finding. Check that the detected stack includes every independent project boundary.
- `SKILL.md:180` — ### Step 4: Validate issue plan
- `SKILL.md:183` — python3 <skill-root>/scripts/repository_hygiene.py issues-validate \
- `SKILL.md:187` — If validation fails, fix the underlying report-to-step mapping or regenerate the plan. Never hand-edit a plan and preserve its old digest.
- `SKILL.md:191` — Display the issue count, titles, destructive flags, repository, source HEAD, and plan digest. When the request explicitly asks to create GitHub issues, that request authorizes issue publication after validation.
- `SKILL.md:214` — - canonical install, build, test, lint, type-check, docs, and release commands;
- `SKILL.md:367` — python3 <skill-root>/scripts/repository_hygiene.py verify \
- `SKILL.md:403` — - `2`: expected operational or validation failure;
- `SKILL.md:418` — - Validation failure: fix, regenerate, validate again; never bypass a failed digest or schema gate.
- `SKILL.md:440` — python3 -m unittest discover -s <skill-root>/tests -v
- `SKILL.md:443` — Only state **Done & Verified** when metadata, direct-reference structure, JSON, Python compilation, tests, issue-plan validation, and package layout all pass with fresh evidence.

### Execution candidates

- `references/portability-security.md:55` — Issue publication needs Issues write permission. Label deletion needs Issues write permission. Ensuring labels may need the same permission. The skill does not modify branch protection, rulesets, repository settings, files, branches, or pull requests.
- `references/portability-security.md:101` — - search for network calls, subprocess execution, credential reads, and destructive commands
- `scripts/audit_repository.py:492` — verification=[f"python -c \"import yaml; yaml.safe_load(open('{path}', encoding='utf-8'))\"", f"actionlint {path}"],
- `scripts/audit_repository.py:829` — actions=["Define a ruleset or branch protection requiring pull requests and appropriate status checks.", "Require reviews according to contributor count and risk.", "Limit bypasses and destructive branch operations.", "Avoid requiring checks that cannot run on all eligible pull requests."],
- `scripts/github_operations.py:326` — body_path.unlink(missing_ok=True)
- `scripts/hygiene_core.py:9` — import subprocess
- `scripts/hygiene_core.py:131` — temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
- `scripts/hygiene_core.py:135` — def write_text(path: Path, value: str) -> None:
- `scripts/hygiene_core.py:138` — temporary.write_text(value, encoding="utf-8")
- `scripts/hygiene_core.py:151` — completed = subprocess.run(
- `scripts/hygiene_core.py:158` — stdout=subprocess.PIPE,
- `scripts/hygiene_core.py:159` — stderr=subprocess.PIPE,
- `scripts/hygiene_core.py:165` — except subprocess.TimeoutExpired as exc:
- `scripts/repository_hygiene.py:130` — write_text(out_dir / "report.md", report_markdown(report))
- `scripts/repository_hygiene.py:143` — write_text(out_dir / "issue-plan.md", issue_plan_markdown(issue_plan))

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
