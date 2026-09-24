# Integration guide: read-the-damn-docs

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

- `README.md:3` — Make agents web-search for the docs before they guess.
- `README.md:7` — It tells the agent when docs are mandatory, why web search is usually the right
- `README.md:15` — - Directs the agent to web-search for current official docs unless the relevant
- `README.md:17` — - Requires current version checks before adding packages or writing install,
- `README.md:23` — - Makes the agent name the docs or files it relied on when that evidence affects
- `README.md:26` — ## When To Use It
- `README.md:28` — Use it when an agent might otherwise rely on stale model memory. Most of the
- `README.md:39` — These should trigger docs before code:
- `SKILL.md:3` — description: "Require current authoritative documentation before using third-party APIs, libraries, frameworks, CLIs, or services."
- `SKILL.md:13` — - [When A Quick Local Read Is Enough](#when-a-quick-local-read-is-enough)
- `SKILL.md:14` — - [If Docs Are Unavailable](#if-docs-are-unavailable)
- `SKILL.md:19` — pages, and read them before coding. For APIs, versions, provider behavior,
- `SKILL.md:25` — Read docs before proceeding when any of these are true:
- `SKILL.md:58` — search when you do not already have the exact URL.
- `SKILL.md:59` — - Package registry metadata for versions. Before adding a dependency, query

### Verification candidates

- `SKILL.md:79` — internal code, then official upstream docs. For new packages, verify the
- `SKILL.md:86` — 6. Verify with the smallest useful check: typecheck, tests, build, CLI dry run,
- `SKILL.md:87` — API schema validation, or a local reproduction.
- `SKILL.md:93` — - "Add Tailwind to this app." Check the current Tailwind major and its install
- `SKILL.md:95` — - "Use the AI SDK to stream responses." Verify the current AI SDK major,
- `VERIFICATION.md:9` — External documentation lookup is host- and network-dependent and is not run as part of validation.

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
