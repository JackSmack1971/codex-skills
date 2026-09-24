# Integration guide: stack-detection

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Wired instrumentation

`SKILL.md`'s `## Telemetry` section wires the following semantic events into
this skill's actual Inspect/Classify/Output structure (superseding the
generic candidate scan below, which is kept only as provenance for why these
points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before Inspect | `run.started` | `task_category` (architectural vs. client-layer vs. general) |
| After Inspect | `verification` (`phase=inspect`) | `evidence_files_found`, `missing_manifests_count` |
| After Classify | `decision` (`phase=classify`) | `classification`, `evidence_file_count` |
| Before returning Output | `run.finished` | `classification`, `follow_on_skills_suggested`, `missing_manifests_count` |
| When a maintainer later overturns the classification | `user.correction` | `original_classification`, `correction`, `corrected_classification` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:3` — description: "Classify a desktop client stack before architectural or client-layer changes." — became the `task_category` enum.
- `SKILL.md:9-15` — the Inspect file list (`package.json`, `src-tauri/Cargo.toml`, `tauri.conf.json`, `docs/`/`.planning/`, source tree) — became `evidence_files_found`.
- `SKILL.md:17-21` — the three classification buckets — became the `classification` enum.
- `SKILL.md:23-32` — the required Output fields (classification, evidence files, missing manifests, follow-on suggestions) — became `missing_manifests_count` and `follow_on_skills_suggested`.

### Execution candidates

- None; this skill has no bundled scripts.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
