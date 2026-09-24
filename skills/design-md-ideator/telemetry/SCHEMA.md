# Telemetry schema for design-md-ideator

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `dd4f31a2fb471a2b6635c6f31cb26e3d5aa9e1b232d446f0f531eaa31c2797fa`

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
- `correlated`: hook-observed execution evidence (tool calls, commands, exit codes) automatically attached to the semantic run that was open in the same session when it fired; included in analysis by default, but is a best-effort session-scoped join, not proof the tool call belongs to this skill's own logic.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence outside any open run; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether the skill is
actually grounding its output in discovered evidence and enforcing its own
strict-profile contract, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`create`, `refine`, `reconstruct`, `validate`) | Which of the description's four operations this run performed. | Lets an improvement agent see whether one mode (e.g. `reconstruct`) fails or stalls disproportionately. |
| `decision` | `discover` | `evidence_sources` | array of enum (`existing_design_md`, `tokens_or_css`, `screenshots_or_brand`, `existing_components`, `user_requirements`) | Which Workflow-step-1 evidence classes were actually found and used. | A run that reaches generation with zero evidence sources is a strong signal the skill guessed instead of discovering. |
| `decision` | `discover` | `ledger_classifications` | object of integer counts (`confirmed`, `recommended`, `assumed`, `conflict`) | Counts by the skill's own required ledger labels. | A chronically high `assumed`/`conflict` share on real projects means the questionnaire (step 2) isn't resolving enough before generation. |
| `decision` | `ledger` | `token_groups_nonempty` | array of enum (`colors`, `typography`, `spacing`, `rounded`, `components`) | Which of the operating contract's "five token groups" were populated before generation. | Directly measures compliance with the skill's own non-negotiable strict-profile rule; a group missing here predicts a validator failure. |
| `decision` | `ledger` | `unresolved_assumptions` / `recommended_defaults` | integer | Ledger items left as agent defaults rather than user-confirmed. | High counts indicate the questionnaire is being skipped rather than driving real decisions. |
| `verification` | `validate` | `exit_code` | integer | `validate_design_md.py --profile strict` result. | The ground-truth check that the "eight canonical sections" and "five token groups" rules actually held. |
| `verification` | `validate` | `retry_count` | integer | Fix-and-revalidate cycles before a clean pass. | A rising retry rate points at a specific, recurring generation defect (e.g. a routinely malformed section) worth fixing in the Generation rules. |
| `run.finished` | `finish` | `sections_completed` | integer | Canonical `##` sections present at delivery (of the required eight). | A value under eight delivered as success means the finish evidence disagrees with the validator — a hook-integrity signal. |
| `run.finished` | `finish` | `assumptions_disclosed` | integer | Assumptions still open at delivery, per the Deliver step's own requirement. | Tracks whether the skill is honestly disclosing gaps versus quietly fabricating brand facts. |

An improvement agent should aggregate `ledger_classifications` and
`token_groups_nonempty` across runs — e.g. which token group is most often
missing, or whether `assumed` counts are rising — to decide whether the
Workflow's discovery or questionnaire steps in `SKILL.md` need revision.
