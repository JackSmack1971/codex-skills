# Telemetry schema for context-doctor

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `89fe937a1d8556df10a55c898f470b155e9b8d999124dabf09a721e8b06c248e`

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
skill's evidence-labeling discipline and finding quality hold up, not just
that an audit ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`static_only`, `with_runtime_telemetry`) | Whether user-supplied Codex runtime telemetry (e.g. `codex exec --json`) was available for the run. | Separates audits limited to static evidence from those that could also measure runtime context effects, per the Scope section. |
| `verification` | `collect` | `collector_completed` | boolean | Whether `context_inventory.py` (step 2) finished successfully. | The collector is the evidence backbone for every later claim; a failed collection invalidates the whole report. |
| `verification` | `collect` | `agents_md_files_found` | integer | `AGENTS.md`/`AGENTS.override.md` files inventoried. | A basic scale signal for the audit surface, useful for comparing report depth across repositories. |
| `verification` | `collect` | `config_layers_detected` | integer | Distinct Codex config layers (user/project/managed/plugin) found. | Confirms step 1's layer-resolution requirement is actually grounded in inventory evidence. |
| `decision` | `label` | `claim_labels_used` | array of enum (`DIRECT`, `MEASURED`, `INFERRED`, `UNKNOWN`) | Which of step 5's required claim labels appear in the report. | Directly measures whether the labeling discipline is applied, or whether the report silently collapses to one label class. |
| `decision` | `label` | `unknown_claim_count` | integer | Claims labeled `UNKNOWN` (e.g. missing telemetry). | The Evidence rules require missing telemetry to be `UNKNOWN`, not a finding; tracks how often the audit is evidence-starved. |
| `decision` | `rank` | `findings_count` | integer | Actionable findings ranked in step 7. | A zero on a repository with detectable Codex control-plane usage may mean ranking under-fired rather than a genuinely clean audit. |
| `decision` | `rank` | `risk_categories` | array of enum (`agents_md`, `skills_discovery`, `config_layers`, `hooks_mcp`, `compaction`, `model_settings`) | Which Scope-section audit areas produced findings. | Reveals whether findings skew toward one audit area regardless of what the repository actually exhibits. |
| `run.finished` | `finish` | `approval_sentence_included` | boolean | Whether the Completion section's required approval sentence was emitted. | Directly checks Completion-section compliance ("End with the report contract's required approval sentence"). |
| `user.correction` | — | `finding_category`, `correction` | string | A maintainer later dismissing a finding, reclassifying a claim's label, or disputing a stated burden. | The ground-truth signal for calibration — without it, `rank`/`label` events only show what the audit claimed, not whether it was accurate. |

An improvement agent should join `decision` (`phase=rank`) events against
later `user.correction` events (same `run_id`) to compute a rough
false-positive rate per `risk_categories` value, and watch
`unknown_claim_count` for a rising trend that would indicate the Evidence
rules or collector need to capture more runtime telemetry.
