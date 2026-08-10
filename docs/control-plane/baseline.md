# Pre-control-plane baseline

Recorded on 2026-08-10 before adding any project control-plane files. This is
a documentation-only snapshot; it does not change skill behavior.

## Repository state and layout

- Git branch: `work`
- HEAD: `def28e8` (`Merge pull request #12 from
  JackSmack1971/agent/ci-deterministic-validation`)
- Initial worktree: clean; there were no unrelated uncommitted changes to
  preserve.
- Top-level tracked/project entries: `.github/`, `.gitignore`, `LICENSE`,
  `README.md`, `benchmarks/`, `docs/`, `scripts/`, `skills/`, and `tests/`.
  (`.git/` is repository metadata.)
- Project-level `AGENTS.md`, `.agents/`, and `.codex/`: absent.
- `codex --version`: unavailable because `codex` was not installed or not on
  `PATH`.

## Inventory

- Skills (`skills/*/SKILL.md`): 50.
- Classifications: 23 Core, 26 Specialized, 0 Experimental, and 1
  Vendored-or-Adapted.
- Evaluation levels: 34 `manual-prose`, 10 `deterministic-validator`, 4
  `automated-behavioral`, and 2 `none`.

The counts can be reproduced from `docs/skill-inventory.md` and
`docs/evaluation-inventory.json`; the repository validator also reports the
total skill count.

## Existing validation commands

The repository's validation command center and CI define these commands:

```text
python scripts/validate_repository.py
python -m unittest discover -s tests -v
python scripts/run_core_benchmark.py --deterministic-only
python scripts/validate_skill_inventory.py
```

## Baseline command results

All requested checks passed before this file was added:

| Command | Result |
|---|---|
| `python scripts/validate_repository.py` | PASS (`SKILLS_VALIDATED=50`; `REPOSITORY_VALIDATION_OK`; all 23 Core evaluation-matrix rows passed all dimensions) |
| `python -m unittest discover -s tests -v` | PASS (9 tests; `OK`) |
| `python scripts/run_core_benchmark.py --deterministic-only` | PASS (23 skills, 69 cases, 0 errors; implicit-selection measurement unavailable because the local JSONL stream does not expose skill selection) |
| `git diff --check` | PASS (no output) |

After this documentation-only addition, the same four commands were rerun and
retained the same pass/fail state: all passed.
