# Integration guide: context-doctor

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Static candidates from the target

These are inspection hints, not runtime facts.

### Decision candidates

- `SKILL.md:28` — - Stop after the report. Remediation is a separate, explicitly approved task.
- `references/audit-playbook.md:12` — Record the repository root, current working directory, `CODEX_HOME`, active profile if supplied, project trust state if supplied, and collector truncation. Distinguish user `CODEX_HOME` files from project `.codex` files. Do not assume a project layer is active merely because it exists.
- `references/audit-playbook.md:16` — Audit `AGENTS.override.md` and `AGENTS.md` files in the Codex home and from the project root to the current directory. Report measured bytes/lines, empty files, duplicate guidance, nested overrides, fallback filenames configured by `project_doc_fallback_filenames`, and the combined `project_doc_max_bytes` limit. Do not call a file “loaded” unless runtime evidence or the documented path chain supports it.
- `references/audit-playbook.md:20` — Audit `.agents/skills` directories discovered from the current directory toward the repository root and the user skill directory `$HOME/.agents/skills`. For each shown skill, collect only name, description characteristics, path, file sizes, and optional directory presence. Codex starts discovery with name, description, and path, caps the initial list at 2% of context or 8,000 characters when unknown, and loads the full `SKILL.md` only after selection. Do not estimate token cost from bytes.
- `references/audit-playbook.md:22` — Inspect `[[skills.config]]` entries in active config layers. If a path is disabled, report the explicit path and status; do not infer the state of unlisted skills. Duplicate names are separate skills, not a merged skill.
- `references/audit-playbook.md:34` — Inventory `hooks.json` and inline `[hooks]` tables in active config layers. Report event names, handler counts/types, `additionalContextLimit` presence, and trust/review status when supplied. Codex documents `SessionStart`, `SubagentStart`, `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `Stop`, and related lifecycle events; configured is not the same as injected. Never emit matcher strings, commands, inputs, outputs, or hook payloads.
- `references/audit-playbook.md:54` — Follow `report-contract.md` exactly. Stop after reporting. No remediation is performed by this skill.
- `references/portability-security.md:7` — Project `.codex` configuration and hooks are trusted only when Codex trusts the project layer. The skill reports trust-sensitive configuration as observed or UNKNOWN; it does not change trust, approvals, sandbox mode, rules, or hooks.
- `references/portability-security.md:9` — No MCP connector, plugin manifest, UI file, or external service is required by this skill. If a future change adds one, its exact Codex schema must be documented first and the collector must preserve the same redaction boundary.
- `references/report-contract.md:3` — Produce this structure unless the user explicitly requests another format.
- `references/report-contract.md:9` — State repository root, current directory, `CODEX_HOME`, active profile if known, project trust state if known, Codex config layers inspected, runtime telemetry availability, and collector truncation.
- `references/report-contract.md:40` — 4. expected context effect, qualitative unless runtime telemetry measures it;
- `references/report-contract.md:46` — Report supplied Codex runtime telemetry only. If absent, say UNKNOWN. Never infer current context utilization or cache behavior from file size.
- `scripts/context_inventory.py:52` — if not lines or lines[0].strip() != "---":
- `scripts/context_inventory.py:56` — if line.strip() == "---":

### Verification candidates

- `VERIFICATION.md:3` — Target package validation:
- `VERIFICATION.md:12` — Validation on 2026-08-09:
- `VERIFICATION.md:15` — - Missing-path collector smoke check → bounded JSON; no file bodies, raw environment values, MCP endpoints/headers, hook payloads, transcripts, or token estimates.
- `VERIFICATION.md:16` — - Real-repository collector smoke check with `--codex-home .codex --repo . --cwd .` → completed successfully; `.codex` was absent/empty and the collector reported that state without reading unrelated files.
- `VERIFICATION.md:18` — - In this no-Git workspace, a live `codex exec` smoke test reported the newly migrated `$review-agent` skill as not discoverable even though the collector inventories `.agents/skills`; repository-skill discovery is not proven in this environment.
- `scripts/validate_skill.py:2` — """Validate the portable Context Doctor package."""

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
