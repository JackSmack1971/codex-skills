# Integration guide: openai-docs

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Wired instrumentation

`SKILL.md`'s `## Telemetry` section wires the following semantic events into
this skill's actual source-order and routing steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before the first substantive action | `run.started` | `task_category` (route guessed from the request) |
| After the first substantive action (search, then fetch/open) | `verification` (`phase=search`) | `source_order_followed`, `official_domain`, `page_fetched` |
| After "Choose one primary route" | `decision` (`phase=route`) | `route`, `reference_read`, `requested_model_preserved` |
| Before returning the answer | `run.finished` | `route`, `citations_count`, `uncertainty_disclosed` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11` — "Complete this source order before reading a reference... or answering from memory" — became `source_order_followed`.
- `SKILL.md:11` — "Use the actual fetched page, not a search snippet or an unopened link" — became `page_fetched`.
- `SKILL.md:11` — "Preserve the exact requested model; never substitute a newer model" — became `requested_model_preserved`.
- `SKILL.md:19-27` — "Choose one primary route" bullet list (local documentation integration, model migration, model selection, product/API docs, codex self-knowledge) — became the `route`/`task_category` enum, with a residual `direct_citation_no_route` value for the straightforward-request carve-out described at `SKILL.md:17`.
- `SKILL.md:33` — supported official surfaces list (`developers.openai.com`, `platform.openai.com`, `help.openai.com`, `learn.chatgpt.com`, `openai.com`) — became the `official_domain` enum.
- `SKILL.md:33` — "State uncertainty when first-party sources do not establish pricing, availability, account access, limits, or behavior" — became `uncertainty_disclosed`.

### Execution candidates

- `scripts/fetch-codex-manual.mjs` and `scripts/resolve-latest-model-info` remain uninstrumented directly; they are exercised only under the `codex_self_knowledge`/`model_migration` routes and their outcomes surface through the `route` and `page_fetched` fields above, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
