# Integration guide: using-git-worktrees

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

- `SKILL.md:11` — - **Trigger and exclusion:** Use when isolated Git worktree setup or verification is requested or genuinely required for parallel branch work; exclude complete issue-to-PR lifecycle, routing to github-issue-to-pr.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:21` — Use this skill only when isolation is requested or parallel implementation genuinely needs it. First detect `.worktrees/` or `worktrees/`, then verify ignore status, construct a branch path, create the worktree, optionally run the project's existing setup, and run its existing baseline tests. Stop with structured output on a missing Git repository, branch collision, setup failure, or test failure.
- `scripts/worktree.py:24` — if args.command == "detect":
- `scripts/worktree.py:26` — print(json.dumps({"status": "FOUND_BOTH" if dot and plain else "FOUND_DOTWORKTREES" if dot else "FOUND_WORKTREES" if plain else "NOT_FOUND", "location": ".worktrees" if dot else "worktrees" if plain else None}))
- `scripts/worktree.py:28` — if args.command == "path":
- `scripts/worktree.py:30` — if root.returncode:
- `scripts/worktree.py:35` — output = location / project / args.branch if raw_location.startswith("~") else location / args.branch
- `scripts/worktree.py:37` — if args.command == "verify-ignore":
- `scripts/worktree.py:39` — print(json.dumps({"status": "IGNORED" if result.returncode == 0 else "NOT_IGNORED", "dir": args.dir})); return 0
- `scripts/worktree.py:40` — if args.command == "create":
- `scripts/worktree.py:41` — if git("rev-parse", "--show-toplevel").returncode:
- `scripts/worktree.py:44` — if exists and not args.no_create_branch:
- `scripts/worktree.py:46` — command = ["worktree", "add", args.path] + ([args.branch] if args.no_create_branch else ["-b", args.branch])

### Verification candidates

- `SKILL.md:3` — description: "Create or verify an isolated Git worktree for parallel or branch-isolated work; github-issue-to-pr composes it for the complete lifecycle."
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:21` — Use this skill only when isolation is requested or parallel implementation genuinely needs it. First detect `.worktrees/` or `worktrees/`, then verify ignore status, construct a branch path, create the worktree, optionally run the project's existing setup, and run its existing baseline tests. Stop with structured output on a missing Git repository, branch collision, setup failure, or test failure.
- `SKILL.md:30` — python scripts/worktree.py test --path <path>
- `SKILL.md:31` — python scripts/worktree.py verify-ignore --dir .worktrees
- `scripts/worktree.py:11` — return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
- `scripts/worktree.py:20` — for name in ("setup", "test"): p = sub.add_parser(name); p.add_argument("--path", required=True)
- `scripts/worktree.py:21` — ignore = sub.add_parser("verify-ignore"); ignore.add_argument("--dir", required=True)
- `scripts/worktree.py:37` — if args.command == "verify-ignore":
- `scripts/worktree.py:38` — result = git("check-ignore", "-q", args.dir)
- `scripts/worktree.py:43` — exists = git("show-ref", "--verify", "--quiet", f"refs/heads/{args.branch}").returncode == 0
- `scripts/worktree.py:54` — print(json.dumps({"status": "NO_TEST_RUNNER", "count": 0, "failures": 0, "note": "Run the project's documented baseline test command."})); return 0
- `tests/evaluation-cases.md:3` — 1. **Normal:** Given parallel branch work, create and verify an isolated worktree with the expected branch and path.
- `tests/evaluation-cases.md:5` — 3. **Boundary:** Given a cleanup request, verify the exact worktree and branch state before removal.

### Execution candidates

- `scripts/worktree.py:6` — import subprocess
- `scripts/worktree.py:10` — def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
- `scripts/worktree.py:11` — return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
