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

## Wired instrumentation

`SKILL.md`'s `## Telemetry` section wires the following semantic events into
this skill's actual numbered Workflow steps (superseding the generic
candidate scan below, which is kept only as provenance for why these points
were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before step 1 | `run.started` | `task_category` (`static_only`\|`with_runtime_telemetry`) |
| After step 2 (run the bundled collector) | `verification` (`phase=collect`) | `collector_completed`, `agents_md_files_found`, `config_layers_detected` |
| After step 5 (label claims) | `decision` (`phase=label`) | `claim_labels_used`, `unknown_claim_count` |
| After step 7 (rank actionable findings) | `decision` (`phase=rank`) | `findings_count`, `risk_categories` |
| Before returning the report (after step 8) | `run.finished` | `findings_count`, `unknown_claim_count`, `approval_sentence_included` |
| When a maintainer later disputes a finding | `user.correction` | `finding_category`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and the false-positive-rate analysis an improvement agent should run over
these fields.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:9` — "inspect only documented Codex control-plane files and runtime evidence" plus the Scope section's "User-supplied Codex runtime evidence ... optional" — became the `task_category` enum.
- `SKILL.md:36` — the `context_inventory.py` collector invocation — became `collector_completed`.
- `SKILL.md:41` — "Label claims DIRECT, MEASURED, INFERRED, or UNKNOWN" — became `claim_labels_used`/`unknown_claim_count`.
- `SKILL.md:43` — "State risk, rollback, and the approval boundary for each proposal" and the finding-ranking step — became `findings_count`/`risk_categories`.
- `SKILL.md:11-18` — the Scope section's four audit areas (AGENTS.md, skills, config/hooks, runtime evidence) — became the `risk_categories` enum.
- `SKILL.md:63` — "End with the report contract's required approval sentence" — became `approval_sentence_included`.

### Execution candidates

- `scripts/context_inventory.py` and `scripts/validate_skill.py` remain uninstrumented directly; their outcomes are captured through the `collect`-phase `verification` event above instead of per-subprocess-call instrumentation, per the "high-value semantic boundaries only" principle.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
