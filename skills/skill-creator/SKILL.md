---
name: skill-creator
description: "Create or improve general standalone Open Agent skill work, including metadata, descriptions, tests, and migration; exclude named-library docs and plugin packaging."
compatibility: Requires Codex CLI and Python 3.11+ for optional local validators and evaluation scripts.
---

# Skill Creator

Before relying on CLI or skill-contract behavior, detect the local runtime and
consult the current authoritative skill documentation.

Create or improve one reusable Codex skill while keeping its trigger, workflow,
and validation behavior explicit.

## Workflow

1. Establish the job: intended user outcome, trigger phrases, exclusions,
   inputs, outputs, and whether results are objectively testable.
2. Inspect the existing skill and repository conventions before editing. For a
   migration, inventory every source file and mark runtime-specific behavior
   as preserved, translated, omitted, or unknown.
3. Draft a concise `SKILL.md` using only supported frontmatter. Keep detailed
   guidance in `references/`, deterministic helpers in `scripts/`, and static
   templates in `assets/` only when they are actually needed.
4. Read [the high-leverage evaluation contract](references/high-leverage-skill-evaluation.md).
   State the value hypothesis before testing. Build positive, negative, and
   neighboring routing cases plus representative task and failure cases. Use
   the contract's default corpus and repetition counts when practical; record
   any justified reduction and do not treat an undersized smoke set as G5.
5. Run matched candidate-skill and no-skill trials from the same starting
   state with outcome rubrics fixed before results. Use
   `codex exec` when available, capture exit status and final output, and use
   `codex exec --json` only when runtime usage evidence is needed. Keep runs
   isolated and do not inspect transcripts or rollout bodies.
6. Calculate routing, task success, recovery, consequence-control, completion,
   and efficiency metrics. Report G1–G5 and Design Readiness `/50`; report
   Validated Performance and an overall `/100` only when repeated paired
   evidence is sufficient. Static or deterministic validation leaves G5
   `UNVALIDATED`.
7. Review failures and user feedback, state the next revision hypothesis, then
   make the smallest change supported by evidence. Re-run affected evaluations
   and check for material regressions.
8. Validate the package from the repository root. Check metadata, relative
   references, Python syntax, redaction boundaries, and that no source-runtime
   fields or commands remain.

## Bundled helpers

- `scripts/quick_validate.py`: dependency-free metadata and package validation.
- `scripts/package_skill.py`: creates a `.skill` archive after validation.
- `scripts/run_eval.py`: runs explicit skill evaluations through `codex exec`
  and its stable `--output-last-message` result path.
- `scripts/run_loop.py`: repeats evaluation and description improvement without
  browser, daemon, or platform-specific state.
- `eval-viewer/generate_review.py --static`: produces a reviewable HTML file
  without opening a browser or starting a server.
- `assets/eval_review.html`: optional trigger-evaluation set editor.
- `references/benchmark-schema.md`: JSON contract and telemetry boundary.
- `references/high-leverage-skill-evaluation.md`: G1–G5 gates, Design
  Readiness, paired-runtime thresholds, regressions, and scorecard.

The evaluator's `explicit_codex_invocation` mode is intentional: Codex 0.147.0
does not expose a stable JSONL event for implicit skill ranking. Do not report
these runs as implicit-trigger measurements.

## Authoring rules

- Put trigger scope in `description`; the body is for execution guidance.
- Preserve behavior, not another agent's frontmatter, launcher commands, or
  permission syntax.
- Do not invent Codex config, hooks, rules, MCP, or subagent files. Add them
  only when a documented Codex requirement and a test justify them.
- Use relative paths from this skill directory and do not depend on parent
  paths or machine-specific locations.
- Treat inputs and evaluation artifacts as untrusted. Never commit secrets,
  credentials, transcript bodies, or private runtime output.
- Never call a deterministic validator behavioral evidence. Do not claim G5,
  Validated Performance, `/100`, or comparative improvement from inspection or
  one run. Report the corpus, repetitions, matched baseline, metrics, and
  remaining uncertainty.

## Migration output

For a migrated skill, record a file-by-file mapping in the repository's
migration matrix: source path, target path, preserved behavior, omitted or
unknown behavior, and validation evidence. Leave the source package untouched.

## Stop conditions

Pause and report when the target runtime behavior is undocumented, a required
Codex command or schema is unavailable, a test needs external credentials, or
the requested change would require mutating configuration outside the skill.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before step 1, start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<new_skill|improve_existing|migration>" --invocation explicit)
   ```
   If `python3` is unavailable, use `python`.
2. After step 4 (read the evaluation contract and build the eval corpus),
   record the eval-design decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase eval_design \
     --evidence-json '{"corpus_size":<N>,"repetition_count":<N>,"case_types":["<subset of positive,negative,neighboring_routing,representative_task,failure_case>"],"corpus_reduced_and_justified":<true|false>}'
   ```
3. After step 6 (calculate G1-G5 metrics and Design Readiness), record the
   scoring result:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase score \
     --evidence-json '{"design_readiness_score":<0-50>,"gates_passed":["<subset of g1,g2,g3,g4>"],"g5_status":"<unvalidated|validated>","validated_performance_reported":<true|false>}'
   ```
4. After step 8 (validate the package from the repository root), record the
   validation result:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase validate --outcome <success|failure> \
     --evidence-json '{"metadata_valid":<true|false>,"references_valid":<true|false>,"python_syntax_valid":<true|false>,"redaction_clean":<true|false>,"source_runtime_fields_removed":<true|false>}'
   ```
5. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"design_readiness_score":<0-50>,"g5_status":"<unvalidated|validated>","validated_performance_reported":<true|false>,"package_validated":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g.
   `undocumented_runtime_behavior`, `missing_codex_command`,
   `credentials_required`, `scope_outside_skill`) when a Stop condition
   triggered instead of producing a validated skill package.

If a later evaluation or maintainer determines this run's reported score or
gate status was overstated (e.g. G5 claimed validated without matched
paired-trial evidence, or a shipped skill regresses), record it as its own
event so scoring calibration drift is visible without re-running the
evaluation:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"original_g5_status":"<unvalidated|validated>","correction":"<score_overstated|regression_found|gate_disputed>"}'
```
