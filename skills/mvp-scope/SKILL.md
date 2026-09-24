---
name: mvp-scope
description: "Use to turn a product idea or capability list into explicit must-have, later, and won't-build scope decisions before specification or architecture. Do not use to discover the problem or write detailed feature behavior; use product-discovery or product-spec."
compatibility: Requires a product problem, desired outcome, constraints, or feature list.
---

# MVP Scope

Choose the smallest product that proves the intended value loop. Every item
must support a user outcome or a necessary safety/operational constraint.

## Workflow

1. State the user, problem, desired outcome, and MVP success condition.
2. Map each proposed capability to that outcome and note dependencies.
3. Classify items as Must have, Should have, Later, or Explicitly won't build.
4. Remove speculative flexibility, premature scale, admin, multi-tenancy,
   extensibility, and infrastructure that the success condition does not need.
5. Record risks, unresolved decisions, and the smallest end-to-end slice.

## Output

Produce `MVP_SCOPE.md` containing the success condition, included scope,
deferred scope, won't-build list, dependencies, risks, and a definition of
done. State what evidence would justify promoting a deferred item.

## Boundary

Do not silently drop a requested safety, accessibility, compliance, or data-
loss requirement. Flag it as a constraint even when it is not user-visible.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before step 1, start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<problem|desired_outcome|constraints|feature_list>" --invocation "<explicit|implicit|unknown>")
   ```
2. After step 3 (classify items as Must have, Should have, Later, or
   Explicitly won't build), record the classification:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase classify \
     --evidence-json '{"must_have_count":<N>,"should_have_count":<N>,"later_count":<N>,"wont_build_count":<N>}'
   ```
3. After step 4 (remove speculative flexibility, premature scale, admin,
   multi-tenancy, extensibility, and unneeded infrastructure), record the
   trim decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase trim \
     --evidence-json '{"trimmed_categories":["<subset of speculative_flexibility,premature_scale,admin,multi_tenancy,extensibility,infrastructure>"],"items_removed":<N>,"safety_constraint_preserved":<true|false>}'
   ```
4. After step 5 (record risks, unresolved decisions, and the smallest
   end-to-end slice), record verification:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase finalize --outcome success \
     --evidence-json '{"risks_count":<N>,"unresolved_decisions_count":<N>,"end_to_end_slice_defined":<true|false>}'
   ```
5. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"must_have_count":<N>,"wont_build_count":<N>,"promotion_criteria_stated":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` when the workflow stopped
   under Failure/stop instead of producing `MVP_SCOPE.md`.
