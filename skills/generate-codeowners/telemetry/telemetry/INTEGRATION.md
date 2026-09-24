# Integration guide: generate-codeowners

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

- `SKILL.md:18` — Create or audit GitHub CODEOWNERS from repository evidence. Treat `$mode` as `generate` when omitted. Treat `$owner_map` as optional. Only accept `generate` or `audit`.
- `SKILL.md:23` — - Prefer visible GitHub teams with explicit write access. Use an individual only for a personal repository or when the supplied owner map explicitly authorizes that exception.
- `SKILL.md:25` — - Write only `.github/CODEOWNERS`; GitHub checks `.github/` before root and `docs/`.
- `SKILL.md:35` — 3. Repository evidence: tracked files, manifests, architecture, Git history, existing ownership files, governance documents, and read-only GitHub metadata when `gh` is installed and authenticated.
- `SKILL.md:40` — 2. Read `references/design-policy.md`. Read `references/ownership-plan-schema.md` before creating a plan.
- `SKILL.md:64` — 8. In `generate` mode, classify the repository before designing rules:
- `SKILL.md:70` — - small or mixed repository when evidence is insufficient for a stronger classification.
- `SKILL.md:81` — - Keep unit tests with their product domain. Give integration or system test suites a separate QA owner only when the repository structure supports it.
- `SKILL.md:82` — - Use a fallback only when the repository archetype and verified team capacity justify the notification load.
- `SKILL.md:83` — - Add increasingly specific overrides after broad rules.
- `SKILL.md:85` — 12. If any required production domain lacks a verified owner, do not write `.github/CODEOWNERS`. Produce a concise ownership-gap report listing exact paths and the owner roles that must be mapped.
- `SKILL.md:117` — Do not claim success unless the target file exists in generate mode, validation exits zero, `.github/CODEOWNERS` is self-owned, and the working-tree diff is limited to the expected file.
- `SKILL.md:122` — - `PostToolUse`: rerun validation after the target file changes.
- `SKILL.md:126` — Use a documented Codex project hook or rule only when deterministic enforcement is explicitly requested; this skill package does not ship a runtime hook configuration.
- `SKILL.md:134` — - **Generated or vendored files dominate reviews:** add a narrowly scoped blank-owner override only after verifying the path is reproducible and protected against manual edits elsewhere.

### Verification candidates

- `SKILL.md:81` — - Keep unit tests with their product domain. Give integration or system test suites a separate QA owner only when the repository structure supports it.
- `SKILL.md:95` — 15. Validate immediately:
- `SKILL.md:101` — --json-out "$(git rev-parse --git-path codex-codeowners)/validation.json"
- `SKILL.md:117` — Do not claim success unless the target file exists in generate mode, validation exits zero, `.github/CODEOWNERS` is self-owned, and the working-tree diff is limited to the expected file.
- `SKILL.md:122` — - `PostToolUse`: rerun validation after the target file changes.
- `SKILL.md:123` — - `Stop` or `TaskCompleted`: require a zero-error validation result and an expected-only diff.
- `SKILL.md:124` — - `SubagentStop`: return the generated path, validation JSON path, coverage counts, and unresolved warnings.
- `SKILL.md:140` — **[Steps]** Classify as a modular application; place a justified fallback first only when a verified steward team exists; assign product ownership to the service; assign platform ownership to workflows; assign database plus product ownership to migrations; add `.github/CODEOWNERS` self-ownership; validate last-match behavior and coverage.
- `SKILL.md:142` — **[Output]** `.github/CODEOWNERS`, an untracked inventory and validation report under the Git metadata directory, and a final summary identifying ownership sources, exceptions, and ruleset recommendations.
- `VERIFICATION.md:7` — - Windows smoke check: `python scripts/run_python.py scripts/validate_codeowners.py --help`.
- `references/design-policy.md:153` — - validate CODEOWNERS on changes and on a schedule;
- `references/ownership-plan-schema.md:71` — The owner map is evidence, not an instruction to skip repository analysis. Validate each recommended path against tracked files and final precedence.
- `scripts/analyze_repository.py:244` — check=False,
- `scripts/analyze_repository.py:378` — remote_proc = run(["git", "remote", "get-url", "origin"], repo, check=False)
- `scripts/analyze_repository.py:408` — total_commits_proc = run(["git", "rev-list", "--count", "HEAD"], repo, check=False)

### Execution candidates

- `scripts/codeowners_common.py:10` — import subprocess
- `scripts/codeowners_common.py:29` — ) -> subprocess.CompletedProcess[str]:
- `scripts/codeowners_common.py:31` — proc = subprocess.run(
- `scripts/codeowners_common.py:35` — stdout=subprocess.PIPE,
- `scripts/codeowners_common.py:36` — stderr=subprocess.PIPE,
- `scripts/codeowners_common.py:67` — temp.write_text(content, encoding="utf-8", newline="\n")
- `scripts/codeowners_common.py:101` — proc = subprocess.run(
- `scripts/codeowners_common.py:105` — stdout=subprocess.PIPE,
- `scripts/codeowners_common.py:106` — stderr=subprocess.PIPE,
- `scripts/self_test.py:7` — import subprocess
- `scripts/self_test.py:13` — def run(args: list[str], cwd: Path, expected: int = 0) -> subprocess.CompletedProcess[str]:
- `scripts/self_test.py:14` — proc = subprocess.run(args, cwd=str(cwd), check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
- `scripts/self_test.py:33` — (repo / "services/payments/app.py").write_text("print('ok')\n", encoding="utf-8")
- `scripts/self_test.py:34` — (repo / ".github/workflows/ci.yml").write_text("name: CI\n", encoding="utf-8")
- `scripts/self_test.py:35` — (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
