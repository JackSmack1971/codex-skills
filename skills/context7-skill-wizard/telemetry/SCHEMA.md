# Telemetry schema for context7-skill-wizard

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `dd9b4980942b50363200a70edb4ddda7076c90e84156bdde9f06b95f5f9b1917`

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
wired into `SKILL.md`'s Telemetry section. They measure whether this
skill's documentation-grounding and validation discipline hold up, not just
that a skill package was generated.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`single_library`, `multi_library`) | Whether one or several libraries were selected in step 2. | Lets an improvement agent check whether multi-library runs systematically produce more coverage gaps or validation failures. |
| `decision` | `resolve` | `libraries_resolved_count` | integer | Libraries resolved via Context7 `resolve-library-id`. | Confirms step 2 actually resolved every library the user selected before documentation queries began. |
| `decision` | `resolve` | `library_ambiguous` | boolean | Whether multiple matches were presented and the user had to pick among them. | Tracks how often library resolution is ambiguous, informing whether step 2's disambiguation guidance needs sharpening. |
| `verification` | `query` | `topics_queried_count` | integer | Documentation topics queried via `query-docs` in step 4. | Step 3 requires two or three scope questions mapped to topics; a count outside 1-3 per library flags scope-question drift. |
| `verification` | `query` | `empty_query_retried` | boolean | Whether step 4's "retry once with a broader topic" rule fired. | Confirms the retry rule is actually exercised rather than silently giving up on an empty result. |
| `verification` | `query` | `coverage_gaps_count` | integer | Topics recorded as UNKNOWN coverage gaps after retry. | Directly tracks documentation-grounding completeness; a rising count across runs suggests Context7 coverage or topic-derivation needs revision. |
| `verification` | `validate` | `validation_passed` | boolean | `validate_generated_skill.py` (step 7) result. | The completion gate for the generated package; a chronically failing first pass points at a systemic generation defect. |
| `verification` | `validate` | `retry_count` | integer | Validation repair attempts before passing. | A rising retry rate points at a recurring, fixable defect class in skill generation rather than one-off noise. |
| `verification` | `validate` | `body_lines_count` | integer | Non-empty body lines in the generated `SKILL.md`. | Directly checks the Boundaries section's "under 500 non-empty body lines" limit. |
| `run.finished` | `finish` | `libraries_selected_count`, `topics_fetched_count` | integer | Final counts reported in the Completion summary. | Baseline scale metrics for comparing run complexity against `coverage_gaps_count` and `validation_passed`. |

An improvement agent should track `coverage_gaps_count` and
`library_ambiguous` against `task_category`, and watch whether
`validation_passed` first-pass rates fall as `libraries_resolved_count`
grows, to decide whether the Workflow or Boundaries sections of `SKILL.md`
need revision for multi-library runs.
