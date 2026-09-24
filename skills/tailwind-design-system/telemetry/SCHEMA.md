# Telemetry schema for tailwind-design-system

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `1ab23408272be8a4236f0304c361c6a889f74099903a792022c0d6855ac3dcb3`

## Event classes

- `run.started`, `run.finished`
- `skill.invocation`
- `precondition`
- `decision`
- `operation`
- `verification`
- `failure`, `retry`
- `user.correction`, `agent.error`
- `eval.result`, `lesson.candidate`
- `hook.observation`, `usage`

## Attribution

- `semantic`: target-owned event with target fingerprint.
- `confirmed`: imported/correlated evidence known to exercise this skill.
- `correlated`: hook-observed execution evidence (tool calls, commands, exit codes) automatically attached to the semantic run that was open in the same session when it fired; included in analysis by default, but is a best-effort session-scoped join, not proof the tool call belongs to this skill's own logic.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence outside any open run; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They are the fields an
improvement agent should read to judge and improve this specific skill — the
generic event classes above only say *when* something happened; these say
*what actually happened*.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`component_library`, `design_tokens`, `responsive_accessible`, `pattern_standardization`, `migration`, `dark_mode_setup`) | Which "Use this skill when" scenario the request matched. | Lets an improvement agent see which scenarios are most common and whether one correlates with more `version_unknown` stops. |
| `decision` | `version_gate` | `tailwind_version` | enum (`v3`, `v4`, `unknown`) | The version established by the version gate. | The primary correctness-critical decision; every downstream setup pattern depends on this being right. |
| `decision` | `version_gate` | `evidence_source` | enum (`package_json`, `lockfile`, `dependency_tree`, `css_config`, `insufficient`) | Which evidence tier (in the gate's stated priority order) actually resolved the version. | Confirms the gate is preferring `package_json`/lockfile evidence over weaker corroborating evidence, per the stated order. |
| `decision` | `version_gate` | `stopped_due_to_unknown` | boolean | Whether the run stopped before giving version-sensitive guidance because evidence was missing or conflicting. | Tracks how often the "do not silently choose v3 or v4" rule actually has to engage. |
| `operation` | `apply_playbook` | `playbook_loaded` | boolean | Whether `resources/implementation-playbook.md` was opened. | Shows whether the skill is relying on the lean core `SKILL.md` alone or consistently escalating to the full playbook. |
| `operation` | `apply_playbook` | `version_neutral_sections_used` | array of enum (`design_tokens`, `component_variants`, `responsive`, `dark_mode`, `accessibility`) | Which version-neutral guidance areas were actually applied. | Reveals whether requests cluster around a subset of areas the core `SKILL.md` under- or over-serves. |
| `operation` | `apply_playbook` | `mixed_setup_flagged` | boolean | Whether a v3/v4 pattern mix was explicitly explained per "Never mix the two setup patterns without explaining the compatibility reason." | A `false` value on a run that needed it is a direct rule violation to flag. |
| `run.finished` | `finish` | `tailwind_version`, `task_category`, `playbook_loaded` | enum / string / boolean | Final run summary. | Cross-run aggregation of version-gate outcomes and playbook usage without re-reading each session. |
| `user.correction` | — | `original_tailwind_version`, `correction`, `corrected_version` | enum / `"version_misdetected"` / enum | A maintainer later reporting the detected version was wrong. | The ground-truth signal for version-gate accuracy — without it, `tailwind_version` counts only show what the skill claimed, not whether it was right. |

An improvement agent should track the `stopped_due_to_unknown` rate by
`evidence_source`, and join `tailwind_version` against later
`user.correction` events to estimate the version gate's real accuracy — a
persistently high misdetection rate on one evidence tier is a concrete
signal to revise the Version gate section's evidence order.
