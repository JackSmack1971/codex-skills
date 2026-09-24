---
name: grilling
description: "Use for a new interactive plan or design stress-test, asking one recommended question at a time until shared understanding. Do not use for explicit /grill-me compatibility invocations; route those to grill-me."
compatibility: Requires an interactive conversation with user feedback.
---

# Grilling

Interview the user relentlessly about the plan or design until shared understanding is reached.

- Ask exactly one question at a time and wait for the user's answer.
- Walk each design branch in dependency order, resolving decisions before dependent questions.
- Give a recommended answer with every question.
- Explore the codebase when it can answer the question instead of asking the user.
- Do not enact the plan until the user confirms that shared understanding has been reached.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the interview uninterrupted and never let it block or
change the output.

1. Before the first question, start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<plan|design>" --invocation "<explicit|implicit|unknown>")
   ```
2. After the question loop concludes (one question at a time, each with a
   recommended answer, walking branches in dependency order, exploring the
   codebase before asking when possible), record the interview decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase interrogate \
     --evidence-json '{"questions_asked":<N>,"branches_resolved":<N>,"questions_without_recommendation":<N>,"answer_sources":["<subset of codebase_explored,user_asked>"]}'
   ```
3. Before enacting the plan or design, record the confirmation gate:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase confirm --outcome success \
     --evidence-json '{"shared_understanding_confirmed":<true|false>,"plan_enacted":<true|false>}'
   ```
4. Before returning to the user, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"questions_asked":<N>,"branches_resolved":<N>,"shared_understanding_confirmed":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` when the session was
   abandoned before shared understanding was reached.

If the user later rejects a recommended answer this session gave, picks an
alternative other than the one recommended, or says a dependency branch was
missed, record it as its own event so calibration drift is visible without
re-running the skill:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"correction":"<recommendation_rejected|branch_missed>","detail":"<short label>"}'
```

