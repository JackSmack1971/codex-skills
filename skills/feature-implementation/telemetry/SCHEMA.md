# Telemetry schema for feature-implementation

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `564930365f49be16b30ae5e0f51f688ad322d2db4ad09dba72220ed45907286a`

## Event classes

- `run.started`, `run.finished`
- `skill.invocation`
- `precondition`
- `decision`
- `operation`
- `verification`
- `failure`, `retry`
- `user.correction`, `agent.error`
- `eval.result`, `lesson.candidate`
- `hook.observation`, `usage`

## Attribution

- `semantic`: target-owned event with target fingerprint.
- `confirmed`: imported/correlated evidence known to exercise this skill.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether the skill
kept to "the smallest complete behavior" and actually ran its own required
checks, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `decision` | `scope` | `missing_decisions_count` | integer | Gaps identified while reading the specification (step 1). | A persistent zero on ambiguous requests suggests step 1's gap-finding is being skipped rather than performed. |
| `decision` | `scope` | `scope_conflict_flagged` | boolean | Whether a Boundary-level scope conflict was caught and reported. | Confirms the Boundary's "stop and ask when requirements conflict" rule actually fires when it should. |
| `decision` | `implement` | `files_touched` | integer | Files touched by the chosen end-to-end slice. | Outlier-high counts on a routine feature suggest scope crept past "the fewest files it needs." |
| `decision` | `implement` | `layer` | enum (`ui_or_client`, `api_or_service`, `data_or_persistence`, `cross_cutting`) | Which architectural layer (from step 2's inspection) the slice primarily touched. | Lets an improvement agent see whether one layer is disproportionately error-prone or under-tested. |
| `decision` | `implement` | `input_validation_added` / `error_handling_added` / `security_or_accessibility_addressed` | boolean | Whether step 4's required cross-cutting concerns were addressed. | Directly measures compliance with the skill's own step-4 checklist; a chronic `false` on any field is a concrete Workflow gap. |
| `verification` | `verify` | `tests_added_or_updated` | boolean | Whether step 5's "smallest meaningful verification" was added. | A false on a non-trivial change means shipped behavior has no regression protection. |
| `verification` | `verify` | `focused_tests_passed` / `lint_type_checks_passed` | boolean | Result of step 5's required checks. | Separates "the skill verified and it failed" from "the skill never actually ran the checks it claims to run." |
| `run.finished` | `finish` | `files_changed` | integer | Final count of files in the shipped change. | Cross-checked against `files_touched` from the `implement` decision to catch scope drift between planning and delivery. |
| `run.finished` | `finish` | `deferred_work_items` | integer | Count of explicitly deferred items in the final report. | Chronically nonzero counts on "smallest complete behavior" work suggest the Boundary is being stretched. |

An improvement agent should watch the `layer` distribution together with
`focused_tests_passed`/`lint_type_checks_passed` failure rates to see
whether one architectural layer needs a stricter Workflow step, and compare
`files_touched` against `files_changed` to detect scope growth mid-run.
