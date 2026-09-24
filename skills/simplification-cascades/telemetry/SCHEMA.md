# Telemetry schema for simplification-cascades

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `5e2178c65be2e49a9aae0f798476ad8accf5820064bb6cd7952f0ff2e78f07d7`

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
improvement agent should read to judge and improve this specific skill — the
generic event classes above only say *when* something happened; these say
*what actually happened*.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`explicit_target_path`, `default_target_path`) | Whether the run was given a target path or fell back to `.`. | Lets an improvement agent check whether unscoped (`.`) runs correlate with noisier or lower-value cascade signals. |
| `operation` | `scan` | `cascade_score` | integer | The scanner's raw score before any fix. | The primary opportunity-size signal; its distribution shows whether the skill is mostly invoked on high- or low-signal codebases. |
| `operation` | `scan` | `duplicate_patterns_count` / `special_case_hotspots_count` / `config_bloat_files_count` | integer | Counts per Signal-interpretation category. | Reveals which signal type actually drives most runs, so the Signal interpretation table can be reweighted if one category dominates or never fires. |
| `operation` | `scan` | `signals_detected` | boolean | Whether any signal fired at all. | A persistently low rate flags that the skill is being invoked on scopes too narrow or too clean to be useful. |
| `decision` | `abstract` | `elimination_count` | integer | Implementations/special cases the proposed abstraction eliminates. | Directly measures the Workflow's own "at least three" validity bar. |
| `decision` | `abstract` | `cascade_valid` | boolean | Whether `elimination_count >= 3`. | Tracks how often the skill proposes an abstraction that fails its own validity bar. |
| `decision` | `abstract` | `fit_violated_threshold` | boolean | Whether more than 20% of detected cases did not fit the stated abstraction. | Measures how often the required revise-the-abstraction branch (Workflow step 5) actually triggers. |
| `decision` | `abstract` | `signal_types_addressed` | array of enum (`duplicate_patterns`, `special_case_hotspots`, `config_bloat_files`) | Which signal categories the abstraction actually covers. | Shows whether cascades tend to unify only one signal type, suggesting the Workflow should split single-type and multi-type cascade guidance. |
| `verification` | `verify` | `verified` | boolean | Whether a real `--verify` rerun happened after a refactor (Workflow step 7). | A low rate means claims of success are going unverified, contrary to the Boundaries section. |
| `verification` | `verify` | `cascade_score` / `post_cascade_score` | integer | Before/after scores from the rerun. | The ground-truth check that a claimed simplification actually reduced the score, per step 7's explicit requirement. |
| `verification` | `verify` | `score_improved` | boolean | Whether `post_cascade_score < cascade_score`. | A recurring `false` here means the skill is claiming success without evidence, violating "Do not claim success unless the latter is lower." |
| `user.correction` | — | `original_elimination_count`, `correction` | integer / enum (`abstraction_rejected`, `elimination_count_overstated`, `false_positive_signal`) | A maintainer later rejecting the proposed abstraction or its claimed impact. | The ground-truth signal for whether `cascade_valid` runs actually held up under human review. |

An improvement agent should track the rate of `signals_detected=false` runs,
the distribution of `cascade_valid` and `score_improved`, and whether
`verified=false` runs are nonetheless reported as successful, to decide
whether the Workflow or Boundaries sections of `SKILL.md` need revision.
