# Evaluation maturity rubric

The repository uses one evaluation rubric. A skill has exactly one current
level in `docs/evaluation-inventory.json`; the level describes evidence that
exists today, not expected quality or trigger accuracy.

| Level | Name | Evidence allowed |
|---|---|---|
| 1 | `none` | No skill-specific evaluation artifact. |
| 2 | `manual-prose` | Human-reviewed scenarios in `tests/evaluation-cases.md`; these are not automated tests. |
| 3 | `deterministic-validator` | A repeatable validator, fixture test, or self-test with stable pass/fail output. |
| 4 | `automated-behavioral` | An executable target-workflow suite or model-backed evaluation run with outcome assertions. The canonical command must execute that behavior. |

Manual scenarios remain separate from executable tests. The repository makes
no claim about implicit skill selection unless a runtime measurement exists.
Corpus validation, schema checks, fixture grading, and a model-backed runner's
`--deterministic-only` mode are `deterministic-validator` evidence even when the
same runner can perform behavioral trials in another mode. An evidence label
describes what its canonical command actually executes, not what the referenced
script could execute with different arguments.
The delivery validators cover objective artifact invariants only; judgment-heavy
quality such as prioritization, wording, and review completeness remains manual.
Scores and benchmark results are not recorded here.
