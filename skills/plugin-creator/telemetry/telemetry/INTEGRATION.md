# Integration guide: plugin-creator

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

- `SKILL.md:9` — Before relying on manifest fields, commands, or packaging behavior, detect the
- `SKILL.md:24` — 2. Edit `<plugin-path>/.codex-plugin/plugin.json` when the request gives specific metadata.
- `SKILL.md:27` — 3. Generate or update the personal marketplace entry when the plugin should appear in Codex UI ordering:
- `SKILL.md:34` — Only specify `--marketplace-name <name>` when the default `personal` marketplace name is already
- `SKILL.md:43` — Only use a repo/team marketplace when the user specifically asks for that destination:
- `SKILL.md:52` — When the user specifies a marketplace path, make sure that marketplace is actually installed before
- `SKILL.md:69` — 5. Before handing back a generated plugin, run:
- `SKILL.md:82` — Prefer the helper default cachebuster unless the user explicitly asks for a specific override.
- `SKILL.md:93` — - Creates or updates `~/.agents/plugins/marketplace.json` when `--with-marketplace` is set.
- `SKILL.md:94` — - If the marketplace file does not exist yet, seed a personal marketplace root before adding the first plugin entry.
- `SKILL.md:113` — when the user specifically requests it.
- `SKILL.md:114` — - `--marketplace-name` is an exception path. Use it only when the default `personal` marketplace
- `SKILL.md:116` — - Do not use `--marketplace-name` to rename an existing marketplace file in place. If the file
- `SKILL.md:118` — - If the user specifies a different marketplace path, treat that marketplace as needing explicit installation via `codex plugin marketplace add`.
- `SKILL.md:119` — - Prefer `scripts/read_marketplace_name.py` when you need the marketplace name from any

### Verification candidates

- `SKILL.md:10` — installed tooling and verify the current plugin contract.
- `SKILL.md:193` — - Omit unsupported plugin manifest fields that validation rejects, including `hooks`.
- `SKILL.md:203` — and then continue from validation or subsequent plugin edits instead of leaving the workflow
- `SKILL.md:235` — ## Validation
- `VERIFICATION.md:3` — - Python AST check passed for all helper scripts.
- `agents/openai.yaml:4` — default_prompt: "Use $plugin-creator to scaffold a valid plugin in the personal marketplace, then validate it before handing it back."
- `references/installing-and-updating.md:66` — path, and `codex plugin marketplace list` is not the right check for whether that default
- `references/installing-and-updating.md:69` — 4. If the plugin is not using the personal marketplace file, check which configured local
- `references/plugin-json-spec.md:202` — ### Plugin validation notes
- `references/plugin-json-spec.md:219` — intentional preflight check that rejects leftover `[TODO: ...]` placeholders.
- `scripts/create_basic_plugin.py:195` — description="Create a plugin skeleton with a validation-ready plugin.json."
- `scripts/validate_plugin.py:2` — """Validate a generated plugin against the plugin ingestion contract."""
- `scripts/validate_plugin.py:29` — parser = argparse.ArgumentParser(description="Validate a local Codex plugin.")
- `scripts/validate_plugin.py:39` — print("Plugin validation failed:")
- `scripts/validate_plugin.py:43` — print(f"Plugin validation passed: {plugin_root}")

### Execution candidates

- `scripts/create_basic_plugin.py:104` — with path.open() as handle:
- `scripts/create_basic_plugin.py:179` — with path.open("w") as handle:
- `scripts/create_basic_plugin.py:188` — with path.open("w") as handle:
- `scripts/update_plugin_cachebuster.py:44` — manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
