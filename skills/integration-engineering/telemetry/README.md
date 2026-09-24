# Telemetry sidecar: integration-engineering

Generated for target fingerprint `cc43583b3f234d8f401afc24f4f96f4b7b96fc012586584739257a57adc57c93` in `repo` mode.

This directory is an observability/eval substrate, not a self-modification engine.

## Record a semantic run

```bash
RUN_ID=$(python recorder.py start --invocation explicit --task-category example)
python recorder.py event --run-id "$RUN_ID" --event verification --phase verify --outcome success
python recorder.py finish --run-id "$RUN_ID" --outcome success
```

On PowerShell, capture the first command output into a variable instead of using `$(...)`.

## Storage

- `raw/`: semantic runtime events; ignored by VCS by default.
- `ambient/`: optional hook observations; ignored by VCS by default.
- `derived/`: findings/eval candidates worth review.
- `evals/regressions/`: only reviewed/promoted regression artifacts.
- `state/`: local privacy salt, the active-run correlation pointer, and a durable run index (`runs_index.jsonl`); ignored by VCS.
- `tools/`: portable analysis/import/comparison/validation utilities.
- `schemas/`: machine-readable contracts for events, findings, manifests, inspections, and eval candidates.

## Analyze without the generator skill

The sidecar is self-contained for evidence analysis:

```bash
python tools/analyze_telemetry.py .
python tools/derive_eval_cases.py derived/findings.jsonl --out derived/eval-candidates.jsonl --supported-only
python tools/validate_target_telemetry.py .
```

Find the most recent run without the original shell's `$RUN_ID` (for a later `user.correction`, for example):

```bash
python recorder.py last-run
```

If runtime data is redirected with `SKILL_TELEMETRY_DATA_DIR` or `PLUGIN_DATA`, pass its resolved directory to `analyze_telemetry.py --data-root ...`.

When `PLUGIN_DATA` is present, runtime data is written under that writable plugin data directory instead of the installed package root.
