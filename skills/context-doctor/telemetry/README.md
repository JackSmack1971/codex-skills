# Telemetry sidecar: context-doctor

Generated for target fingerprint `89fe937a1d8556df10a55c898f470b155e9b8d999124dabf09a721e8b06c248e` in `repo` mode.

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
- `state/`: local privacy salt and run index; ignored by VCS.
- `tools/`: portable analysis/import/comparison/validation utilities.
- `schemas/`: machine-readable contracts for events, findings, manifests, inspections, and eval candidates.

## Analyze without the generator skill

The sidecar is self-contained for evidence analysis:

```bash
python tools/analyze_telemetry.py .
python tools/derive_eval_cases.py derived/findings.jsonl --out derived/eval-candidates.jsonl --supported-only
python tools/validate_target_telemetry.py .
```

If runtime data is redirected with `SKILL_TELEMETRY_DATA_DIR` or `PLUGIN_DATA`, pass its resolved directory to `analyze_telemetry.py --data-root ...`.

When `PLUGIN_DATA` is present, runtime data is written under that writable plugin data directory instead of the installed package root.
