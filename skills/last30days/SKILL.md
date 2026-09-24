---
name: last30days
description: "Research current public sentiment and trend signals across social, community, and web sources."
license: MIT
---

# last30days

Source and runtime behavior can change. Verify the bundled engine and each
live source contract before treating research results as current.

Use the bundled engine and keep the trigger surface thin.

## What to read

- [Workflow](references/workflow.md) - invocation order, preflight, and engine usage.
- [Output](references/output.md) - report shape, citation rules, and footer requirements.
- [HTML brief](references/save-html-brief.md) - only when the user wants a shareable HTML artifact.

## Core rule

Always run `scripts/last30days.py` for actual research. Do not answer from WebSearch alone.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the research uninterrupted and never let it block or
change the output.

1. Before Workflow step 1 (identify and classify the topic), start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<general|comparison>" --invocation explicit)
   ```
2. After Workflow steps 1-2 (classify the topic; resolve person handles,
   GitHub repos, and communities), record the scoping decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase scope \
     --evidence-json '{"topic_type":"<general|comparison>","entities_resolved":<N>,"plan_file_used":<true|false>}'
   ```
3. After Workflow steps 3-5 (build the query plan, run the bundled engine,
   supplement with WebSearch only when it adds new evidence), record the
   engine verification:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase engine --outcome <success|failure> \
     --evidence-json '{"engine_invoked":<true|false>,"emit_format":"<compact|html>","websearch_supplemented":<true|false>}'
   ```
4. After producing the report (badge, "What I learned:"/comparison title,
   inline citations, engine footer pass-through per `references/output.md`),
   record the output-format check:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase format --outcome <success|failure> \
     --evidence-json '{"badge_present":<true|false>,"citations_inline":<true|false>,"trailing_sources_block_present":<true|false>,"footer_passthrough_verbatim":<true|false>}'
   ```
5. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"topic_type":"<general|comparison>","engine_invoked":<true|false>,"websearch_supplemented":<true|false>,"html_brief_saved":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` when the engine could
   not be run or no topic was provided and the run stopped to ask.

If the user later reports that a cited fact or source in this run's report
was wrong or stale, record it as its own event so research-quality drift is
visible without re-running the skill:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"correction":"<citation_incorrect|stale_finding>","topic_type":"<general|comparison>"}'
```
