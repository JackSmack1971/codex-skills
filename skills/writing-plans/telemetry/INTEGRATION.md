# Integration guide: writing-plans

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

- `SKILL.md:11` — - **Trigger and exclusion:** Use when a concrete implementation plan or task list is requested before coding; exclude direct implementation and vague discovery, routing to feature-implementation or product-discovery.
- `SKILL.md:12` — - **Bounded workflow:** Follow the skill's documented workflow in order, keep changes within the requested scope, and stop when its completion evidence is sufficient.
- `SKILL.md:19` — - **References:** Resolve every required reference and script relative to this skill package; stop if a required bundled resource is absent.
- `SKILL.md:21` — Use this skill when the user asks for a plan, task list, implementation design, or a plan before coding. Extract a short hyphenated feature name, use today's date, and default to `docs/superpowers/plans/` unless the user gives another location.
- `SKILL.md:33` — The validator reports placeholder hits and task count as JSON. Fix every placeholder hit before saving. Do not require `run_command`, shell quoting, a specific shell, a subagent product, or a Git repository; Codex can execute the commands directly and the user chooses the handoff.
- `scripts/plan_tools.py:23` — if args.command == "date":
- `scripts/plan_tools.py:26` — if args.command == "save":
- `scripts/plan_tools.py:30` — if not path.is_file() or not path.stat().st_size:
- `scripts/plan_tools.py:37` — if not path.is_file():
- `scripts/plan_tools.py:41` — hits = [f"{i}:{line}" for i, line in enumerate(lines, 1) if any(p.lower() in line.lower() for p in FORBIDDEN)]
- `scripts/plan_tools.py:42` — result = {"plan_path": str(path), "task_count": sum(line.startswith("### Task ") for line in lines), "placeholder_hits": hits, "placeholder_hit_count": len(hits), "spec_gaps": [], "type_inconsistencies": [], "status": "FAIL" if hits else "PASS"}
- `scripts/plan_tools.py:47` — if __name__ == "__main__":

### Verification candidates

- `SKILL.md:3` — description: "Create concrete TDD-first implementation plans with file maps and validation."
- `SKILL.md:13` — - **Output:** Return the skill's named artifact or decision, with evidence, unresolved assumptions, and validation results.
- `SKILL.md:23` — Keep the plan independently executable: state the goal, architecture, stack, exact files, test-first steps, commands, expected results, and commit boundary. Reject specs that combine unrelated subsystems instead of hiding the split in one oversized plan.
- `SKILL.md:29` — python scripts/plan_tools.py validate --plan-path <path>
- `VERIFICATION.md:3` — - Bash date/save/validation helpers were replaced with `scripts/plan_tools.py`.
- `VERIFICATION.md:4` — - Date, save, and JSON validation commands run on Python 3.14 in this workspace.
- `scripts/plan_tools.py:9` — FORBIDDEN = ("TBD", "TODO", "implement later", "fill in details", "Add appropriate error handling", "add validation", "handle edge cases")
- `scripts/plan_tools.py:16` — validate = sub.add_parser("validate")
- `scripts/plan_tools.py:17` — validate.add_argument("--plan-path", required=True)
- `tests/evaluation-cases.md:3` — 1. **Normal:** Given a feature specification, produce a TDD-first plan with file map, dependencies, and validation commands.

### Execution candidates

- `scripts/plan_tools.py:29` — path.write_text(args.content, encoding="utf-8")

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
