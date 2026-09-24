# Telemetry sidecar: grill-me

Generated for target fingerprint `498e911b452bd1c6a5ea42e3252d12dc5c46d3e0ee938b34c2d6a0e028492a0b` in `repo` mode.

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
