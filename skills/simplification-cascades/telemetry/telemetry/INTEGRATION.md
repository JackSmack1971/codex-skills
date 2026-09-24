# Integration guide: simplification-cascades

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

- `SKILL.md:10` — that collapses multiple components into one. Run the local scan before
- `SKILL.md:15` — 1. Extract a target directory from the request. Use `.` when none is given.
- `SKILL.md:22` — 4. If the score is zero and all lists are empty, report: `No cascade signals
- `SKILL.md:24` — 5. Otherwise, list the variations, state the unifying principle as
- `SKILL.md:26` — cases fit. If more than 20% do not fit, revise the abstraction.
- `SKILL.md:29` — 7. When changes have been applied, rerun with `--verify` and compare the
- `SKILL.md:31` — unless the latter is lower.
- `SKILL.md:43` — configuration details before proposing a refactor. Do not mutate files merely
- `SKILL.md:50` — real before/after target.
- `SKILL.md:59` — least three eliminations, rerun with `--verify` after an actual refactor, and
- `scripts/scan_cascade_signals.py:11` — BRANCH_RE = re.compile(r"^\s*(if|elif|else if|case|switch|catch|except)\b")
- `scripts/scan_cascade_signals.py:17` — path for path in target.rglob("*") if path.is_file() and path.suffix in suffixes
- `scripts/scan_cascade_signals.py:29` — if any(abs(count - seen) < seen // 7 + 1 and count > 20 for seen in seen_counts):
- `scripts/scan_cascade_signals.py:37` — if branches > len(lines) // 8 and branches > 4:
- `scripts/scan_cascade_signals.py:43` — if keys > 50:

### Verification candidates

- `SKILL.md:25` — `Everything here is a special case of [X].`, and test whether all detected
- `SKILL.md:29` — 7. When changes have been applied, rerun with `--verify` and compare the
- `SKILL.md:59` — least three eliminations, rerun with `--verify` after an actual refactor, and
- `VERIFICATION.md:7` — - Preserved: JSON scan fields, score calculation, duplicate/special-case/config heuristics, and verify-mode field.
- `VERIFICATION.md:18` — python .agents/skills/simplification-cascades/scripts/scan_cascade_signals.py --path .agents/skills/simplification-cascades --verify
- `VERIFICATION.md:27` — - Normal and `--verify` scans completed with valid JSON and a zero score on
- `VERIFICATION.md:34` — - The repository TDD runner reports no supported project test runner; direct
- `scripts/scan_cascade_signals.py:21` — def scan(target: Path, verify: bool) -> dict:
- `scripts/scan_cascade_signals.py:54` — "verify_mode": verify,
- `scripts/scan_cascade_signals.py:58` — "post_cascade_score" if verify else "cascade_score": score,
- `scripts/scan_cascade_signals.py:67` — parser.add_argument("--verify", action="store_true")
- `scripts/scan_cascade_signals.py:73` — print(json.dumps(scan(target, args.verify), indent=2))
- `tests/evaluation-cases.md:5` — 3. Run with `--verify`; the score key is `post_cascade_score`.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
