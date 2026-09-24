# Integration guide: changelog-updater

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
- `SKILL.md:39` — 5. Omit internal-only noise unless it changes supported behavior, security, compatibility, performance, packaging, deployment, or documented usage.
- `SKILL.md:43` — 9. When evidence is insufficient, inspect the diff. If ambiguity remains, use conservative wording or omit the entry and record the reason.
- `SKILL.md:57` — - [ ] Apply only after the preview matches intent
- `SKILL.md:63` — Run `git status --short`, identify the repository root, and inspect existing changelog conventions. Detect the project version source when preparing a release. Respect user-supplied date, revision, version, and voice constraints.
- `SKILL.md:65` — Stop if the directory is not a Git worktree. Do not silently initialize a repository.
- `SKILL.md:132` — The writer uses an atomic replacement and creates `CHANGELOG.md.bak` by default when replacing an existing file.
- `SKILL.md:143` — If verification fails, repair the plan or changelog and rerun all relevant checks. Stop after repeated failure and report the exact errors; do not claim success.
- `SKILL.md:152` — | Update after recent work | `since-tag` or `range` | `update_unreleased` |
- `SKILL.md:159` — - “Since last tag” means the latest tag reachable from `HEAD`; if none exists, collect full history and state the fallback.
- `SKILL.md:163` — - Merge commits are excluded by default but their non-merge commits remain available. Include merges only when the merge message carries unique release intent.
- `SKILL.md:176` — Represent breaking changes under the relevant section and prefix the entry with `**Breaking:**`. Do not create a nonstandard top-level category unless the user explicitly requires it.
- `SKILL.md:185` — - Documentation → include only when it materially changes user guidance, migration, setup, or supported behavior
- `SKILL.md:186` — - Chores/tests/CI/dependencies → omit by default; include only when they alter shipped behavior, compatibility, security, packaging, or operator workflow

### Verification candidates

- `SKILL.md:11` — - **Trigger and exclusion:** Use to reconstruct, update, preview, or verify user-facing CHANGELOG.md entries from Git evidence; exclude generic README or release-process work.
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:21` — Turn repository history into a concise, user-facing `CHANGELOG.md`. Codex performs semantic synthesis; bundled scripts perform deterministic collection, validation, mutation, and verification.
- `SKILL.md:55` — - [ ] Validate the plan; fix and repeat until valid
- `SKILL.md:58` — - [ ] Verify the resulting changelog; fix and repeat until valid
- `SKILL.md:101` — ### 4. Validate, preview, and apply
- `SKILL.md:134` — ### 5. Verify
- `SKILL.md:139` — git diff --check -- CHANGELOG.md
- `SKILL.md:155` — | Generate release body without editing | any bounded mode | validate plan, then render dry-run only |
- `SKILL.md:221` — - [ ] `git diff --check -- CHANGELOG.md` exits `0`
- `VERIFICATION.md:17` — - [x] Unit test suite passes: 6 tests, 0 failures
- `resources/cli-contracts.md:10` — {"ok": true, "operation": "validate-plan", "warnings": []}
- `resources/cli-contracts.md:79` — | 4 | Plan or changelog validation error |
- `resources/evaluations.md:7` — History contains `feat`, `fix`, `docs`, `test`, and `chore` commits.
- `resources/evaluations.md:12` — - Test and internal chore are omitted with reasons.

### Execution candidates

- `resources/portability-security.md:34` — Treat third-party modifications to this Skill as software changes. Review every script for subprocess calls, path handling, network access, and write behavior before installation.
- `scripts/apply_changelog.py:344` — temp.write_text(content, encoding="utf-8")
- `scripts/apply_changelog.py:348` — temp.unlink(missing_ok=True)
- `scripts/collect_history.py:9` — import subprocess
- `scripts/collect_history.py:39` — def run_git(repo: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
- `scripts/collect_history.py:40` — process = subprocess.run(
- `scripts/collect_history.py:43` — stdout=subprocess.PIPE,
- `scripts/collect_history.py:44` — stderr=subprocess.PIPE,
- `scripts/collect_history.py:396` — temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
- `scripts/collect_history.py:400` — temp.unlink(missing_ok=True)
- `tests/test_changelog_tools.py:5` — import subprocess
- `tests/test_changelog_tools.py:15` — def run(*args: str, cwd: Optional[Path] = None, expect: int = 0) -> subprocess.CompletedProcess[str]:
- `tests/test_changelog_tools.py:16` — process = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
- `tests/test_changelog_tools.py:25` — path.write_text(
- `tests/test_changelog_tools.py:57` — (root / "app.txt").write_text("one\n", encoding="utf-8")

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
