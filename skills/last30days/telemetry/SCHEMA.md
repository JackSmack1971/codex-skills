# Telemetry schema for last30days

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `51eb5298ad71c2de627a6443f926a457e05c84ecc949716fa3d2697b8d247ff8`

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
calls wired into `SKILL.md`'s Telemetry section. They measure whether the
bundled engine is actually the source of the research and whether the
report follows the skill's own required shape, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`general`, `comparison`) | Whether the request was a single-topic run or a comparison run. | Lets an improvement agent compare research quality and format-check outcomes between `references/output.md`'s two report shapes. |
| `decision` | `scope` | `topic_type` | enum (`general`, `comparison`) | Topic classification result. | Confirms classification happened before the query plan was built, not inferred after the fact. |
| `decision` | `scope` | `entities_resolved` | integer | Count of X/GitHub/subreddit handles resolved during preflight. | A zero count on a people/entity topic signals the "resolve any known X, GitHub, and subreddit scopes before execution" preflight rule was skipped. |
| `decision` | `scope` | `plan_file_used` | boolean | Whether a query-plan tmpfile was built and passed with `--plan`. | Directly measures the "For named entities, always include a plan file" preflight rule. |
| `verification` | `engine` | `engine_invoked` | boolean | Whether `scripts/last30days.py` actually ran. | The primary adherence signal for the Core rule "Always run `scripts/last30days.py` for actual research. Do not answer from WebSearch alone." |
| `verification` | `engine` | `emit_format` | enum (`compact`, `html`) | Which `--emit` mode was used. | Separates ordinary chat runs from HTML-brief runs when interpreting other fields. |
| `verification` | `engine` | `websearch_supplemented` | boolean | Whether WebSearch was used in addition to the engine. | Distinguishes "engine was sufficient" runs from "engine output needed supplementing," per step 5's stated limit ("only when it adds new evidence"). |
| `verification` | `format` | `badge_present` / `citations_inline` / `footer_passthrough_verbatim` | boolean | Whether the required report elements from `references/output.md` were present. | Directly measures adherence to the output contract this skill is required to follow verbatim. |
| `verification` | `format` | `trailing_sources_block_present` | boolean | Whether a disallowed trailing `Sources:` block was added. | Should always be `false`; a `true` value is a direct violation of `references/output.md`. |
| `run.finished` | `finish` | `topic_type` / `engine_invoked` / `websearch_supplemented` | mixed | Run summary. | Cross-run aggregation surface for the fields above. |
| `run.finished` | `finish` | `html_brief_saved` | boolean | Whether an HTML brief was produced per `references/save-html-brief.md`. | Tracks demand for the shareable-artifact path separately from ordinary chat research. |
| `user.correction` | — | `correction`, `topic_type` | string | A user later reporting a cited fact or source was wrong or stale. | The ground-truth signal for research accuracy — without it, `engine_invoked` and format checks only show process compliance, not correctness. |

An improvement agent should watch `engine_invoked` for any `false` runs
(a direct Core-rule violation), track `trailing_sources_block_present` and
`footer_passthrough_verbatim` for output-contract drift, and join
`user.correction` against `topic_type` to see whether general or comparison
runs are more prone to inaccurate findings.
