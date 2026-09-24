# Integration guide: last30days

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
`references/workflow.md`'s Flow and `references/output.md`'s report contract
(superseding the generic candidate scan below, which is kept only as
provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before workflow Flow step 1 (identify and classify topic) | `run.started` | `task_category` (`general` \| `comparison`) |
| After Flow steps 1-2 (classify topic; resolve handles) | `decision` (`phase=scope`) | `topic_type`, `entities_resolved`, `plan_file_used` |
| After Flow steps 3-5 (build plan, run engine, supplement with WebSearch) | `verification` (`phase=engine`) | `engine_invoked`, `emit_format`, `websearch_supplemented` |
| After producing the report per `references/output.md` | `verification` (`phase=format`) | `badge_present`, `citations_inline`, `trailing_sources_block_present`, `footer_passthrough_verbatim` |
| Before returning output | `run.finished` | `topic_type`, `engine_invoked`, `websearch_supplemented`, `html_brief_saved` |
| When a user later disputes a cited fact | `user.correction` | `correction`, `topic_type` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:22` — Core rule "Always run `scripts/last30days.py` for actual research. Do not answer from WebSearch alone." — became `engine_invoked`.
- `references/workflow.md:7-11` — Flow steps 1-5 (identify/classify topic, resolve handles, build query plan, run engine, supplement with WebSearch only when it adds new evidence) — became `topic_type`, `entities_resolved`, `plan_file_used`, `websearch_supplemented`.
- `references/workflow.md:26-29` — Preflight rules ("always include a plan file" for named entities; "resolve any known X, GitHub, and subreddit scopes") — became `plan_file_used`, `entities_resolved`.
- `references/output.md:5-13` — "General runs" report shape (badge, `What I learned:`, inline citations, no trailing `Sources:` block) and "Comparison runs" section — became `topic_type`, `badge_present`, `citations_inline`, `trailing_sources_block_present`.
- `references/output.md:20-24` — Footer rule "Pass through the engine footer verbatim... Keep the final invitation line intact." — became `footer_passthrough_verbatim`.
- `references/save-html-brief.md:11` — "ONLY if the user asked. Do NOT save HTML when the user didn't ask for it." — became `html_brief_saved`.

### Execution candidates

- `scripts/last30days.py` and `scripts/briefing.py` remain uninstrumented directly; their outcomes are captured through the `engine`/`format`/`finish` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
