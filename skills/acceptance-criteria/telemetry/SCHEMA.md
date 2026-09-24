# Telemetry schema for acceptance-criteria

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `629fd07c25eaf30278cc3ae1b0662e8dd7a16ae8e18092a8a5474d789bf7f696`

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

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. They are the fields an
improvement agent should read to judge and improve this specific skill —
the generic event classes above only say *when* something happened; these
say *what actually happened*.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `decision` | `express` | `format` | `"gherkin"` \| `"precise-statement"` | Which criterion format the run produced. | Reveals whether the skill defaults to one format regardless of fit, or adapts to the requirement. |
| `decision` | `express` | `criteria_count` | integer | Number of criteria emitted. | Outlier-low counts on complex requirements suggest under-coverage; trending counts over time show drift. |
| `decision` | `express` | `coverage_classes` | array of enum (`happy_path`, `validation_failure`, `boundary`, `empty_state`, `loading_state`, `error_state`, `permission`, `retry_recovery`) | Which Workflow-step-2 categories were actually covered. | Directly measures whether the skill follows its own required coverage checklist; missing classes are concrete gaps to fix in the skill's Workflow section. |
| `verification` | `check` | `contradictions_found` | integer | Contradictions caught during self-check. | A persistent zero across many runs on complex inputs may mean the check is not actually being performed. |
| `verification` | `check` | `untestable_flagged` | integer | Untestable-language instances caught. | Same rationale — validates the self-check is substantive rather than pro forma. |
| `verification` | `check` | `missing_actor_flagged` | boolean | Whether a missing-actor gap was caught. | Same rationale. |
| `run.finished` | `finish` | `unresolved_questions` | integer | Count of unresolved questions returned to the user. | High or rising counts indicate the skill is being invoked on inputs it cannot fully resolve — a signal for tightening the Trigger/exclusion boundary or the requesting prompt. |
| `run.finished` | `finish` | `out_of_scope_items` | integer | Count of explicitly out-of-scope behaviors named. | Tracks scope discipline; a chronically empty field on ambiguous requirements is suspicious. |

An improvement agent examining `raw/*.jsonl` (or `derived/findings.jsonl`
after running `tools/analyze_telemetry.py`) should aggregate these fields
across runs — e.g. median `criteria_count`, the distribution of
`coverage_classes`, and the rate of nonzero `unresolved_questions` — to
decide whether the Workflow or Boundary sections of `SKILL.md` need
revision.
