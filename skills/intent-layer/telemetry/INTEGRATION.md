# Integration guide: intent-layer

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

- `README.md:37` — ## When to Use
- `README.md:39` — Use intent-layer when:
- `README.md:56` — 1. **Detect** - Check if Intent Layer exists
- `SKILL.md:32` — Has root file → Add Intent Layer section + child nodes if needed
- `SKILL.md:39` — 6. Maintenance mode (when state=complete)
- `SKILL.md:46` — ## When to Create Child Nodes
- `SKILL.md:55` — Do NOT create for: every directory, simple utilities, test folders (unless complex).
- `SKILL.md:59` — When documenting existing code, ask:
- `references/capture-protocol.md:27` — - "What must always be true here? What would break if violated?"
- `references/capture-protocol.md:38` — - "What should never be done, even if the code allows it?"
- `references/capture-protocol.md:47` — When creating parent nodes:
- `references/capture-protocol.md:55` — Before finalizing a node:
- `references/node-examples.md:9` — - [Before (~800 tokens)](#before-800-tokens)
- `references/node-examples.md:10` — - [After (~250 tokens)](#after-250-tokens)
- `references/node-examples.md:81` — ### Before (~800 tokens)

### Verification candidates

- `README.md:56` — 1. **Detect** - Check if Intent Layer exists
- `README.md:64` — - `intent_tools.py detect-state` - Check Intent Layer state
- `SKILL.md:37` — Validate: one root, READ-FIRST directive, <4k tokens per node
- `SKILL.md:55` — Do NOT create for: every directory, simple utilities, test folders (unless complex).
- `SKILL.md:68` — - `scripts/intent_tools.py detect-state` - Check Intent Layer state (none/partial/complete)
- `references/capture-protocol.md:71` — → Purpose: Owns payment lifecycle: initiation → validation → processing → settlement.
- `references/node-examples.md:49` — Owns payment lifecycle: initiation → validation → processing → settlement.
- `references/templates.md:47` — - Don't bypass validation layer

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
