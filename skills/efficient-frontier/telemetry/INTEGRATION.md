# Integration guide: efficient-frontier

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
this skill's actual Workflow steps and named sections (superseding the
generic candidate scan below, which is kept only as provenance for why these
points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before Workflow step 1 | `run.started` | `task_category` (Common Scenarios domain) |
| After Workflow step 3 (spawn parallel subagents) | `decision` (`phase=delegate`) | `subagents_spawned`, `delegated_domains`, `stop_conditions_specified` |
| After Review Loop | `verification` (`phase=review`) | `cited_files_reopened`, `disagreements_resolved`, `high_risk_diffs_skimmed` |
| Before presenting the result | `run.finished` | `delegated_domains`, `subagents_spawned`, `guardrail_violations` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:46-59` — the "Common Scenarios" list (Research, Coding, Testing, Debugging) — became the `task_category`/`delegated_domains` enum.
- `SKILL.md:25-30` — the Handoff Packets requirement to include stop conditions — became `stop_conditions_specified`.
- `SKILL.md:32-37` — the "Useful stop conditions" list — informed the `guardrail_violations`/failure framing at `finish`.
- `SKILL.md:41-44` — the Review Loop's "reopen important cited files, skim high-risk diffs, and rerun or spot-check" — became `cited_files_reopened` and `high_risk_diffs_skimmed`.
- `SKILL.md:44` — "If delegated agents disagree, resolve the disagreement at the frontier-model layer" — became `disagreements_resolved`.
- `SKILL.md:63-68` — the Guardrails list (no same-file concurrent edits, no blind trust on high risk, no universal-savings claims) — became `guardrail_violations`.

### Execution candidates

- None: this skill has no bundled scripts and no numbered `Failure/stop`
  section (its equivalent is `## Guardrails`, referenced by the `finish`
  call's failure guidance); delegated-agent behavior is captured at the
  `delegate`/`review` orchestration boundary instead of per-subagent.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
