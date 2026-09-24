# Telemetry schema for skill-auditor

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `de12529a9bc3f3f55e4d9253fa3bd44190e39840d161b0484dd8a3899d20df9e`

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
wired into `SKILL.md`'s Telemetry section. They measure this meta-skill's
core job — producing traceable, well-calibrated audit findings about another
skill package — not just that an audit ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`quick-trace`, `standard-audit`, `workflow-audit`, `self-audit`, `remediation-plan`) | The Operating mode selected. | Lets an improvement agent check whether one mode systematically produces fewer findings, more corrections, or more gate bypasses than others. |
| `decision` | `gate` | `proceeded_without_questions` | boolean | Whether the context-sufficiency gate (step 2) was satisfied without asking the user anything. | A chronically low rate suggests the gate's three conditions are too strict for real targets; a chronically `true` rate on ambiguous targets suggests the gate is being skipped. |
| `decision` | `gate` | `questions_asked_count` | integer | Size of the compact question batch, if any. | Detects drift toward asking more than "the missing, decision-critical questions." |
| `decision` | `gate` | `missing_grounding_source` | boolean | Whether no grounding source (declared intent, acceptance criteria, workflow contract, or authorized defaults) was available. | Flags audits proceeding on defaults alone — a known confidence-lowering condition the skill itself calls out. |
| `verification` | `evidence` | `verified_quote_count` / `verified_observation_count` / `reported_count` / `estimated_count` / `unknown_count` | integer | Counts of findings tagged `[VERIFIED: QUOTE]`, `[VERIFIED: OBSERVATION]`, `[REPORTED]`, `[ESTIMATED]`, `[UNKNOWN]` in the rule-and-evidence ledger. | Directly measures whether the audit is evidence-first (per step 4) or leaning on inference; a high `estimated_count`/`unknown_count` ratio across runs flags an auditor that is guessing rather than reading. |
| `decision` | `findings` | `h_findings` / `m_findings` / `l_findings` | integer | Finding counts by severity (High/Medium/Low). | Detects drift toward severity inflation or, per the Evidence and severity rules, unjustified deflation. |
| `decision` | `findings` | `lenses_applied` | array of enum (`discovery_metadata`, `progressive_disclosure`, `rule_fidelity`, `workflow_determinism`, `output_contracts`, `executable_code`, `integration_handoffs`, `security_trust`, `portability`, `evaluation_coverage`) | Which audit lenses (step 5) actually fired. | Reveals whether audits are covering the full lens set the rubric expects or narrowing to a habitual subset. |
| `verification` | `validate` | `checklist_failed_count` | integer | How many step-8 checklist items failed on first pass. | A high, non-decreasing rate over time indicates the report-drafting step (step 7) itself needs revision, not just repeated revalidation. |
| `verification` | `validate` | `revalidated` | boolean | Whether the validate-fix-revalidate loop (step 8) actually completed successfully. | Confirms the skill's own completion criteria were met rather than assumed. |
| `run.finished` | `finish` | `mode`, `h_findings`, `m_findings`, `l_findings`, `remediation_requested` | string / integer / boolean | Final mode and finding tally, and whether a remediation plan was requested. | Summarizes run outcome for cross-run aggregation without re-reading the full report. |
| `user.correction` | — | `original_severity`, `correction`, `finding_id` | string / enum (`finding_dismissed`, `severity_adjusted`, `audit_overturned`) | A maintainer later dismissing a finding or overturning the audit's assessment. | The ground-truth signal for whether this auditor's severity calibration and findings hold up under human review. |

An improvement agent should join `decision` (`phase=findings`) events against
later `user.correction` events (same `run_id`) to estimate a per-severity
false-positive rate, and watch the `evidence` phase's tag mix for drift
toward `estimated_count`/`unknown_count` — a sign the Audit workflow or its
resources need revision to make more evidence directly verifiable.
