# Telemetry schema for openai-docs

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `c7debc40a4a62b1a26dcc4c0f0d7fe3b6e646a462044dfea89fd6e7e6e7d2111`

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
wired into `SKILL.md`'s Telemetry section. They measure whether this skill
actually follows its own docs-before-memory source order and route
discipline, not just that a lookup happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`local_integration`, `model_migration`, `model_selection`, `product_api_docs`, `codex_self_knowledge`, `direct_citation_no_route`) | Which "Choose one primary route" bucket the request fell into at start. | Lets an improvement agent see whether certain routes are invoked far more/less than expected, or drift over time. |
| `verification` | `search` | `source_order_followed` | boolean | Whether search-then-fetch happened before reading a reference, local files, or answering from memory. | Directly measures the skill's core required behavior ("Complete this source order before..."); a low rate is the single biggest quality risk for this skill. |
| `verification` | `search` | `official_domain` | enum (`developers.openai.com`, `platform.openai.com`, `help.openai.com`, `learn.chatgpt.com`, `openai.com_product_docs`, `other`) | Which official surface was actually used. | Flags drift toward non-authoritative or wrong-surface sources. |
| `verification` | `search` | `page_fetched` | boolean | Whether an actual page was opened/fetched vs. only a search snippet. | Enforces "Use the actual fetched page, not a search snippet or an unopened link." |
| `decision` | `route` | `route` | enum (same as `task_category`) | The route actually taken, which may differ from the one guessed at start. | Detects route mis-selection, e.g. reading `model-migration.md` for a plain selection question. |
| `decision` | `route` | `reference_read` | boolean | Whether a route reference file was opened at all. | The skill requires reading at most one reference only when "demonstrably needed"; tracks over- or under-reading. |
| `decision` | `route` | `requested_model_preserved` | boolean | Whether an explicitly requested model was preserved rather than silently substituted. | Directly measures compliance with "Preserve the exact requested model; never substitute a newer model." |
| `run.finished` | `finish` | `citations_count` | integer | Number of official citations included in the final answer. | A chronically zero count on non-trivial questions suggests answers are being given from memory despite the docs-first mandate. |
| `run.finished` | `finish` | `uncertainty_disclosed` | boolean | Whether the answer stated uncertainty when first-party sources didn't establish pricing/availability/behavior. | Directly measures compliance with the stated uncertainty-disclosure rule. |

An improvement agent should watch the rate of `source_order_followed ==
false` and `page_fetched == false` as the primary regression signal, and
cross-tabulate `route` against `citations_count` to see which routes tend to
under-cite.
