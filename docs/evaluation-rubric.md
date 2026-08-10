# Evaluation maturity rubric

The repository uses one evaluation rubric. A skill has exactly one current
level in `docs/evaluation-inventory.json`; the level describes evidence that
exists today, not expected quality or trigger accuracy.

| Level | Name | Evidence allowed |
|---|---|---|
| 1 | `none` | No skill-specific evaluation artifact. |
| 2 | `manual-prose` | Human-reviewed scenarios in `tests/evaluation-cases.md`; these are not automated tests. |
| 3 | `deterministic-validator` | A repeatable validator, fixture test, or self-test with stable pass/fail output. |
| 4 | `automated-behavioral` | An executable behavioral suite or model-backed evaluation runner with assertions. |

Manual scenarios remain separate from executable tests. The repository makes
no claim about implicit skill selection unless a runtime measurement exists.
The delivery validators cover objective artifact invariants only; judgment-heavy
quality such as prioritization, wording, and review completeness remains manual.
Scores and benchmark results are not recorded here.
