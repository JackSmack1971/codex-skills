# Telemetry schema for brainstorming-ux-features

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `0eca3b5dcc8e1532517cd29a93db894537aec0cbf9e5503ba462b128a5ad7d40`

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
wired into `SKILL.md`'s Telemetry section. They measure whether this
skill's ideation and selection actually follow its own gates and scoring
model, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`ideas_only`, `specification_only`, `full_workflow`) | Which Mode-outputs mode was requested. | Lets an improvement agent check whether one mode systematically produces weaker evidence grounding or thinner candidate sets. |
| `decision` | `generate` | `candidate_count` | integer | Number of candidates generated in step 2. | The Defaults section requires 5-8; counts outside that range flag under- or over-generation. |
| `decision` | `generate` | `opportunity_classes_covered` | array of enum (`friction_removal`, `discoverability_onboarding`, `feedback_visibility`, `user_control_recovery`, `accessibility`, `personalization`, `collaboration_continuity`, `trust_privacy`) | Which step-2 opportunity classes the candidates actually spanned. | Detects drift toward variants of one idea instead of spanning the required opportunity classes. |
| `decision` | `generate` | `candidates_rejected_count` | integer | Candidates dropped per step 2's rejection criteria (cosmetic, duplicate, unmeasurable, invented demand, rewrite-only). | A persistent zero on a large candidate set suggests the rejection filter isn't being applied. |
| `decision` | `score` | `min_gates_failed_count` | integer | Candidates eliminated by step 3's minimum gates. | Confirms the gate-first ordering in step 3 is actually enforced before scoring. |
| `decision` | `score` | `top_score` | number | Winning candidate's total score (0-100). | Tracks whether selected features clear a meaningful bar over time. |
| `decision` | `score` | `tie_break_applied` | boolean | Whether the manual tie-break order (step 3) was invoked. | Confirms the required manual review runs when `score_candidates.py`'s numeric sort alone is insufficient (scores within 3 points). |
| `verification` | `validate` | `validation_status` | enum (`valid`, `invalid`) | `validate_feature_brief.py --strict` result from step 6. | The primary completion gate; a chronically `invalid` first pass points at a systemic gap in feature-design coverage. |
| `verification` | `validate` | `retry_count` | integer | Validation repair attempts before reaching `valid`. | A rising retry rate points at a recurring, fixable defect class (e.g. missing state coverage) rather than one-off noise. |
| `run.finished` | `finish` | `blocking_questions_count` | integer | Count reported in the required "Blocking questions" output line. | Directly tracks the Output rules' final response format; a rising count signals the skill is being invoked on inputs it can't fully resolve. |
| `user.correction` | — | `original_selection`, `correction`, `work_item_id` | string | A stakeholder later selecting a different candidate, disputing the score, or resolving an open question differently than its `default_if_unanswered`. | The ground-truth signal for calibration — without it, `decision` events only show what the skill picked, not whether it was the right pick. |

An improvement agent should join `decision` (`phase=score`) events against
later `user.correction` events (same `run_id`) to see how often the
highest-scoring candidate is overturned, and watch
`opportunity_classes_covered` for drift toward a narrow subset of the
Candidate-generation opportunity classes.
