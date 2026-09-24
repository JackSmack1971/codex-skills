---
name: grill-me
description: "Compatibility alias for grilling. Use only when the user explicitly invokes /grill-me; for a new interactive plan or design stress-test, use grilling."
compatibility: Requires the `grilling` skill to be available.
---

# Grill Me

Use the `grilling` skill for the session. Challenge assumptions, expose
missing constraints, test alternatives, and keep questioning until the plan or
design is materially sharper.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the session uninterrupted and never let it block or
change the output.

1. Before starting the interrogation, start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<plan|design>" --invocation "<explicit|implicit|unknown>")
   ```
2. After the questioning has run its course (assumptions challenged, missing
   constraints exposed, alternatives tested), record the interrogation
   decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase interrogate \
     --evidence-json '{"questions_asked":<N>,"assumptions_challenged":<N>,"constraints_exposed":<N>,"alternatives_tested":<N>,"answer_sources":["<subset of codebase_explored,user_asked>"]}'
   ```
3. Before enacting the plan or design, record the confirmation gate:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase confirm --outcome success \
     --evidence-json '{"materially_sharper":<true|false>,"shared_understanding_confirmed":<true|false>}'
   ```
4. Before returning to the user (or handing off to enact the plan/design),
   close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"questions_asked":<N>,"materially_sharper":<true|false>,"shared_understanding_confirmed":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` when the session was
   abandoned before shared understanding was reached.

If the user later rejects a recommended answer this session gave, or says
the interrogation missed a branch or constraint, record it as its own event
so drift is visible without re-running the skill:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"correction":"<recommendation_rejected|branch_missed|constraint_missed>","detail":"<short label>"}'
```
