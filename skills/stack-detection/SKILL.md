---
name: stack-detection
description: "Classify a desktop client stack before architectural or client-layer changes."

---

# Stack Detection

Inspect:

- `package.json` or other frontend build manifests
- `src-tauri/Cargo.toml` and Rust entrypoints
- `src-tauri/tauri.conf.json`
- `docs/` and `.planning/`
- the actual source tree under `src/` and `src-tauri/src/`

Classify:

- `docs-first-scaffold`: architecture is described in docs but not yet enforced by runnable app code
- `tauri-desktop-app`: backend/runtime wiring is present and the app is buildable
- `mixed-or-partial`: the project has some runtime wiring but still carries important scaffold gaps

Output:

- Chosen classification
- Evidence files
- Missing build or runtime manifests
- Follow-on skill suggestions:
  - `privacy-boundary-review`
  - `provider-routing-review`
  - `storage-recovery-review`
  - `release-evidence-review`

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before inspecting evidence, start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<architectural_change|client_layer_change|general_classification>" --invocation explicit)
   ```
   If `python3` is unavailable, use `python`.
2. After the Inspect step, record which evidence sources were actually
   found:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase inspect \
     --evidence-json '{"evidence_files_found":["<subset of package_json,cargo_toml,tauri_conf,docs_or_planning,source_tree>"],"missing_manifests_count":<N>}'
   ```
3. After the Classify step, record the classification decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase classify \
     --evidence-json '{"classification":"<docs-first-scaffold|tauri-desktop-app|mixed-or-partial>","evidence_file_count":<N>}'
   ```
4. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"classification":"<docs-first-scaffold|tauri-desktop-app|mixed-or-partial>","follow_on_skills_suggested":["<subset of privacy-boundary-review,provider-routing-review,storage-recovery-review,release-evidence-review>"],"missing_manifests_count":<N>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g.
   `insufficient_evidence`) when the source tree cannot be classified with
   the available evidence.

If a maintainer later determines the classification was wrong, record it as
its own event so drift in this skill's judgment is visible without
re-running the inspection:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"original_classification":"<docs-first-scaffold|tauri-desktop-app|mixed-or-partial>","correction":"classification_overturned","corrected_classification":"<docs-first-scaffold|tauri-desktop-app|mixed-or-partial>"}'
```
