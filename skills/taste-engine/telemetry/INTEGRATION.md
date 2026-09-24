# Integration guide: taste-engine

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

- `SKILL.md:9` — This is an opt-in design aid, not an always-on worker. Use it only when the user explicitly enables it and provides a JSON profile. Read the profile, select the strongest signals for fonts, colors, layout density, and aesthetic direction, and add them as suggestions to the current design brief.
- `SKILL.md:11` — Never invent a profile, infer preferences from hidden session history, write to a legacy runtime config file, or mutate a file without an explicit path and user approval. Current-turn instructions always win. Preserve the supplied JSON schema when the user explicitly requests an approved/rejected update; otherwise return a proposed JSON patch or design-token block rather than writing state.

### Verification candidates

- None detected statically.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
