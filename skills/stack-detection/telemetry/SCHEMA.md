# Telemetry schema for stack-detection

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `d3a9a2b05c0aaec3fada0603cf3dbaa1c666133dbd942a1c19a10ae4250249ec`

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
wired into `SKILL.md`'s Telemetry section. They are the fields an
improvement agent should read to judge and improve this specific skill — the
generic event classes above only say *when* something happened; these say
*what actually happened*.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`architectural_change`, `client_layer_change`, `general_classification`) | Why the classification was requested, per the skill's own description. | Lets an improvement agent check whether one trigger context correlates with a particular classification or with more corrections. |
| `verification` | `inspect` | `evidence_files_found` | array of enum (`package_json`, `cargo_toml`, `tauri_conf`, `docs_or_planning`, `source_tree`) | Which of the five named evidence sources were actually present and inspected. | Directly measures whether the Inspect step's file list is being followed in full or partially skipped. |
| `verification` | `inspect` | `missing_manifests_count` | integer | Count of expected build/runtime manifests that were absent. | Feeds directly into the required "Missing build or runtime manifests" output field; tracks how often classification happens on an incomplete evidence set. |
| `decision` | `classify` | `classification` | enum (`docs-first-scaffold`, `tauri-desktop-app`, `mixed-or-partial`) | The chosen classification. | The primary output signal; its distribution shows whether the skill defaults toward one bucket regardless of evidence. |
| `decision` | `classify` | `evidence_file_count` | integer | How many evidence sources supported the classification. | Low-evidence classifications (e.g. one file) are a concrete flag for low-confidence output that should be reported as such. |
| `run.finished` | `finish` | `follow_on_skills_suggested` | array of enum (`privacy-boundary-review`, `provider-routing-review`, `storage-recovery-review`, `release-evidence-review`) | Which follow-on skills were actually suggested. | Checks that the required Output section's follow-on suggestions are consistently produced rather than omitted. |
| `user.correction` | — | `original_classification`, `correction`, `corrected_classification` | enum / `"classification_overturned"` / enum | A maintainer later disputing the classification. | The ground-truth signal for classification accuracy — without it, `classification` counts only show what the skill claimed, not whether it was right. |

An improvement agent should track the `classification` distribution against
`evidence_file_count` and `missing_manifests_count` (low-evidence runs
producing confident classifications are a red flag), and join `classification`
against later `user.correction` events to estimate a per-class accuracy rate
that would justify revising the Classify section's criteria.
