---
name: efficient-frontier
description: "Orchestrate high-cost frontier-model work through cheaper delegated research, coding, and testing with final synthesis and review."

---

# Efficient Frontier

Use the expensive frontier model where its marginal judgment matters. Push
repeatable, bounded, or token-heavy work to cheaper/faster subagents.

## Workflow

1. Identify the frontier-only decisions: architecture, prioritization,
   ambiguity resolution, risk, synthesis, and final review.
2. Identify delegable work: research scans, repository inventory, search, docs
   extraction, browser/testing passes, log reduction, test failure clustering,
   narrow coding, and mechanical edits.
3. Spawn parallel subagents for independent slices with clear ownership,
   bounded scope, verification gates, and expected evidence.
4. Require compact returns: findings, changed files, commands run, residual
   risk, stop conditions hit, and anything the frontier model must decide.
5. Integrate and review centrally before presenting the result.

## Handoff Packets

Write delegated prompts as self-contained packets. Assume the receiving agent
has not seen the conversation. Include the repo path, objective, scope,
out-of-scope areas, relevant files or search targets, expected return format,
verification commands, and stop conditions.

Useful stop conditions:

- The live code does not match the assumption in the handoff.
- A verification command fails twice after a reasonable fix or retry.
- The work appears to require files outside the assigned scope.
- The agent cannot produce concrete evidence for its claim.

## Review Loop

Treat delegated output as evidence to inspect, not a verdict to forward. Reopen
important cited files, skim high-risk diffs, and rerun or spot-check the
verification that matters before claiming completion. If delegated agents
disagree, resolve the disagreement at the frontier-model layer.

## Common Scenarios

Use these as soft suggestions:

- Research: delegate broad repo scans, docs extraction, and source comparison;
  the frontier model keeps the judgment about what matters.
- Coding: delegate bounded patches, refactors, or mechanical edits when file
  ownership is clear; integrate and review centrally.
- Testing: let the frontier model choose the validation strategy and scripts,
  then use cheaper agents to run unit checks, browser flows, screenshots, and
  log reduction. Ask them to return exact commands, failures, likely causes, and
  whether the signal looks flaky, environmental, or product-relevant.
- Debugging: send independent agents after separate theories, logs, or repro
  paths; keep the final diagnosis with the frontier model.

## Guardrails

- Do not delegate the immediate blocker if your next step depends on it.
- Do not ask multiple agents to edit the same files at the same time.
- Do not trust subagent conclusions blindly when the risk is high; inspect the
  important evidence yourself.
- Do not claim universal savings. The pattern works best when exploration and
  implementation, testing, or research can be parallelized.

## Default Framing

"I will use the frontier model as the orchestrator and reviewer, and use
cheaper subagents for token-heavy research, coding, or testing so the expensive
tokens go to judgment, synthesis, and final quality."

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before Workflow step 1, start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<research|coding|testing|debugging|mixed>" --invocation explicit)
   ```
2. After Workflow step 3 (spawn parallel subagents for independent slices),
   record the delegation decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase delegate \
     --evidence-json '{"subagents_spawned":<N>,"delegated_domains":["<subset of research,coding,testing,debugging>"],"stop_conditions_specified":<true|false>}'
   ```
3. After the Review Loop (treat delegated output as evidence to inspect),
   record the verification pass:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase review --outcome <success|failure> \
     --evidence-json '{"cited_files_reopened":<true|false>,"disagreements_resolved":<N>,"high_risk_diffs_skimmed":<true|false>}'
   ```
4. Before presenting the integrated result, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"delegated_domains":["<subset of research,coding,testing,debugging>"],"subagents_spawned":<N>,"guardrail_violations":<N>}'
   ```
   Use `--outcome failure` with a `--failure-class` when a Guardrail was
   violated (e.g. the same file edited by multiple agents, or a subagent
   conclusion was forwarded unverified) instead of a clean integration.
