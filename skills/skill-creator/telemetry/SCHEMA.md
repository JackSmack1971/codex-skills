# Telemetry schema for skill-creator

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `ad02fc8880eaf6d52b0b8a6d723b7a68e204d1fb6009589e3d085273ebcc6285`

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
wired into `SKILL.md`'s Telemetry section. They measure this meta-skill's
core job — producing or improving another skill with honest, evidence-backed
quality claims — not just that a create/improve session happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`new_skill`, `improve_existing`, `migration`) | Which kind of skill-authoring work was requested. | Lets an improvement agent check whether migrations or improvements have systematically worse validation or scoring outcomes than fresh authoring. |
| `decision` | `eval_design` | `corpus_size` / `repetition_count` | integer | Size and repetition count of the built eval corpus (step 4). | Detects drift toward undersized smoke tests being silently treated as sufficient, contrary to "do not treat an undersized smoke set as G5." |
| `decision` | `eval_design` | `case_types` | array of enum (`positive`, `negative`, `neighboring_routing`, `representative_task`, `failure_case`) | Which required case categories (step 4) were actually built. | Directly measures whether the skill follows its own required test-case coverage rather than only positive cases. |
| `decision` | `eval_design` | `corpus_reduced_and_justified` | boolean | Whether a reduced corpus was used and the reduction was recorded, per step 4. | Flags unjustified corpus shrinkage, which invalidates later G5 claims. |
| `verification` | `score` | `design_readiness_score` | integer (0-50) | The static Design Readiness score from step 6. | Tracks whether authored/improved skills are clearing a reasonable static bar before any runtime claim is made. |
| `verification` | `score` | `gates_passed` | array of enum (`g1`, `g2`, `g3`, `g4`) | Which static gates (routing, decision value, observable completion, failure/autonomy controls) passed. | Shows which gate most often fails, pointing at a recurring authoring weakness (e.g. G4 failure-handling is chronically missing). |
| `verification` | `score` | `g5_status` | enum (`unvalidated`, `validated`) | Whether empirical, paired-trial evidence actually supports G5. | The skill explicitly forbids inflating G5 from inspection alone; this field lets an improvement agent audit whether that rule is honored. |
| `verification` | `score` | `validated_performance_reported` | boolean | Whether a Validated Performance `/100` was reported. | Should almost never be `true` without `g5_status=validated`; a mismatch is a direct rule violation to flag. |
| `verification` | `validate` | `metadata_valid` / `references_valid` / `python_syntax_valid` / `redaction_clean` / `source_runtime_fields_removed` | boolean | Step-8 package validation checks. | Each `false` identifies exactly which pre-ship check is failing most often across authored skills, guiding which validator or instruction needs strengthening. |
| `run.finished` | `finish` | `design_readiness_score`, `g5_status`, `validated_performance_reported`, `package_validated` | integer / enum / boolean | Final scoring and validation summary. | Cross-run aggregation of authored-skill quality without re-reading each package. |
| `user.correction` | — | `original_g5_status`, `correction` | enum (`unvalidated`, `validated`) / enum (`score_overstated`, `regression_found`, `gate_disputed`) | A later evaluation or maintainer disputing this run's reported score or gate status. | The ground-truth signal for whether this skill's own scoring claims are trustworthy over time. |

An improvement agent should watch the `g5_status`/`validated_performance_reported`
pair for rule violations (claiming performance without validation), track the
`gates_passed` distribution for a chronically-failing gate, and join
`verification` (`phase=score`) against later `user.correction` events to
gauge how often this skill's own quality claims hold up.
