# Integration guide: tailwind-design-system

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
this skill's actual version-gate and playbook flow (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before the version gate | `run.started` | `task_category` ("Use this skill when" scenario) |
| After the version gate | `decision` (`phase=version_gate`) | `tailwind_version`, `evidence_source`, `stopped_due_to_unknown` |
| After applying the matched v3/v4 playbook section | `operation` (`phase=apply_playbook`) | `playbook_loaded`, `version_neutral_sections_used`, `mixed_setup_flagged` |
| Before returning output | `run.finished` | `tailwind_version`, `task_category`, `playbook_loaded` |
| When a maintainer later disputes the detected version | `user.correction` | `original_tailwind_version`, `correction`, `corrected_version` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the accuracy analysis (`tailwind_version` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11-18` — the version-gate evidence priority (`package.json`/lockfile, dependency tree, CSS/config as corroborating-only) — became `evidence_source`.
- `SKILL.md:20-21` — "say that the version is unknown and stop... Do not silently choose v3 or v4" — became `stopped_due_to_unknown` and the `version_unknown` failure class.
- `SKILL.md:25-33` — the v3/v4 playbook branches and "never mix the two setup patterns without explaining the compatibility reason" — became `mixed_setup_flagged`.
- `SKILL.md:30-32` — the version-neutral guidance areas (design tokens, component variants, responsive, dark mode, accessibility) — became `version_neutral_sections_used`.
- `SKILL.md:37-44` — the "Use this skill when" scenario list — became the `task_category` enum.
- `SKILL.md:56-57` — "open `resources/implementation-playbook.md` after the version gate succeeds" — became `playbook_loaded`.

### Execution candidates

- None; this skill has no bundled scripts.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
