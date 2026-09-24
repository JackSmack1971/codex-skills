# Integration guide: generate-codeowners

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
this skill's actual Procedure steps (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (`generate`/`audit`) |
| After step 7 (audit mode: report parser errors, dead rules, shadowing, gaps) | `verification` (`phase=audit`) | `parser_errors`, `dead_rules_found`, `shadowing_detected`, `unowned_paths_count`, `individual_owner_risks` |
| After steps 8-12 (generate mode: classify, resolve owners, design map, check gaps) | `decision` (`phase=design`) | `archetype`, `owner_resolution_sources`, `unowned_domains_blocked_generation`, `dual_team_paths` |
| After steps 15-16 (generate mode: validate, fix, revalidate) | `verification` (`phase=validate`) | `exit_code`, `retry_count`, `self_owned`, `diff_scope_expected_only` |
| Before returning the completion contract | `run.finished` | `mode`, `archetype`, `unowned_paths_count`, `validation_exit_code` |
| When a maintainer later overturns an assignment | `user.correction` | `original_assignment`, `correction`, `archetype` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the calibration analysis (`decision` joined against later
`user.correction`) an improvement agent should run over these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:18` — `generate`/`audit` mode distinction — became `task_category`/`mode`.
- `SKILL.md:64-70` — the six repository-archetype classifications — became the `archetype` enum.
- `SKILL.md:71-75` — the owner-resolution evidence order (owner map, existing teams, GitHub teams, personal owner) — became `owner_resolution_sources`.
- `SKILL.md:85` — "do not write `.github/CODEOWNERS`" on an unresolved production-domain gap — became `unowned_domains_blocked_generation`.
- `SKILL.md:62` — audit mode's required report (parser errors, dead rules, shadowing, unowned paths, individual-owner risks) — became the `audit`-phase fields.
- `SKILL.md:117` — the Completion-contract success conditions (file exists, validation exits zero, self-owned, expected-only diff) — became `self_owned`/`diff_scope_expected_only`/`validation_exit_code`.

### Execution candidates

- `scripts/analyze_repository.py`, `scripts/discover_github_owners.py`, and `scripts/render_codeowners.py` remain uninstrumented directly; their outcomes are captured through the `design`/`validate` events above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
