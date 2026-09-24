---
name: simplification-cascades
description: "Find one unifying insight that removes duplicated logic, special cases, or redundant components."
compatibility: Requires Python 3.11+; the bundled scanner is read-only.
---

# Simplification Cascades

Act as a Simplification Cascade Analyst. Find the single unifying abstraction
that collapses multiple components into one. Run the local scan before
reasoning from static context alone.

## Workflow

1. Extract a target directory from the request. Use `.` when none is given.
2. Run the bundled scanner from this skill directory:

   `python scripts/scan_cascade_signals.py --path <TARGET_PATH>`

3. Parse its JSON output: `duplicate_patterns`, `special_case_hotspots`,
   `config_bloat_files`, and `cascade_score`.
4. If the score is zero and all lists are empty, report: `No cascade signals
   detected in the target scope. Consider expanding the search path.`
5. Otherwise, list the variations, state the unifying principle as
   `Everything here is a special case of [X].`, and test whether all detected
   cases fit. If more than 20% do not fit, revise the abstraction.
6. State how many distinct implementations or special cases the abstraction
   eliminates. A valid cascade eliminates at least three.
7. When changes have been applied, rerun with `--verify` and compare the
   initial `cascade_score` with `post_cascade_score`. Do not claim success
   unless the latter is lower.

## Signal interpretation

| Signal | Starting hypothesis |
|---|---|
| `duplicate_patterns` | Abstract the common pattern |
| `special_case_hotspots` | Find the general case with no exceptions |
| `config_bloat_files` | Find defaults that satisfy most cases |
| Score above 70 | Prioritize the opportunity with the largest elimination count |

The scanner is heuristic evidence, not proof. Confirm file, function, and
configuration details before proposing a refactor. Do not mutate files merely
to make the verification score fall.

## Boundaries

The scanner is read-only and bounded to the requested path. Do not execute
project code, install dependencies, or claim a refactor was verified without a
real before/after target.

## Delegation template

`TASK: Simplification Cascade Analysis`

`TARGET_PATH: <user-specified path or .>`

Run the scanner, parse its JSON, identify the unifying abstraction, confirm at
least three eliminations, rerun with `--verify` after an actual refactor, and
return the evidence plus an implementation plan.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before step 1, start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python "<skill-dir>/telemetry/recorder.py" start --task-category "<explicit_target_path|default_target_path>" --invocation "<explicit|implicit|unknown>")
   ```
2. After step 3 (parse the scanner's JSON output), record the scan signal
   profile:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event operation --phase scan \
     --evidence-json '{"cascade_score":<N>,"duplicate_patterns_count":<N>,"special_case_hotspots_count":<N>,"config_bloat_files_count":<N>,"signals_detected":<true|false>}'
   ```
3. After steps 5-6 (state the unifying abstraction, test the 20% fit
   threshold, and count eliminations), record the abstraction decision:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase abstract \
     --evidence-json '{"elimination_count":<N>,"cascade_valid":<true|false>,"fit_violated_threshold":<true|false>,"signal_types_addressed":["<subset of duplicate_patterns,special_case_hotspots,config_bloat_files>"]}'
   ```
4. After step 7 (rerun with `--verify`), record the verification outcome:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase verify --outcome <success|failure> \
     --evidence-json '{"verified":<true|false>,"cascade_score":<N>,"post_cascade_score":<N>,"score_improved":<true|false>}'
   ```
5. Before returning output, close the run:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"cascade_valid":<true|false>,"elimination_count":<N>,"verified":<true|false>,"score_improved":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g. `no_cascade_detected`,
   matching step 4's empty-signal report) when the workflow stopped under
   Boundaries instead of producing a refactor recommendation.

If a maintainer later rejects the proposed abstraction or finds the claimed
elimination count overstated, record it as its own event so drift in this
skill's judgment is visible without re-running the scan:
```bash
python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"original_elimination_count":<N>,"correction":"<abstraction_rejected|elimination_count_overstated|false_positive_signal>"}'
```
