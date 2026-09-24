# Telemetry schema for test-driven-development

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `945501b59c5c7e7265fac8cd9b52b761e15897408bce212cce0f12c6b2b7b4f3`

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

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. They measure whether the
red-green-refactor cycle is genuinely followed, not just whether a run
happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`feature`, `bug_fix`, `refactor`, `test_change`) | Which kind of change the TDD cycle covers. | Lets an improvement agent see whether cycle adherence (e.g. `stages_reached`) drops for particular change types. |
| `verification` | `red` | `stage_result` | enum (`FAIL_CORRECT`, `PASS_UNEXPECTED`, `ERROR`) | Outcome of `scripts/run_tdd_cycle.py --stage red`. | A rising `PASS_UNEXPECTED`/`ERROR` rate shows the "genuine failure required before implementation" gate is not actually being enforced. |
| `verification` | `red` | `runner_detected` | enum (`pytest`, `vitest`, `jest`, `npm_test`, `none`) | Which test runner the helper detected. | A rising `none` rate flags an environment/detection gap in the helper, separate from cycle-discipline issues. |
| `verification` | `red` | `mocks_used` | boolean | Whether the new test relied on mocks. | Checks the bundled anti-pattern guidance ("mock only external or nondeterministic boundaries") is actually followed. |
| `verification` | `green` | `stage_result` | enum (`ALL_PASS`, `TARGET_FAIL`, `REGRESSION`, `ERROR`) | Outcome of `--stage green`. | `REGRESSION` spikes show the "smallest change" claim is not holding up against the full suite. |
| `verification` | `green` | `retry_count` | integer | Green-stage reruns needed before `ALL_PASS`. | High counts indicate the implementation step is not actually minimal on the first attempt. |
| `verification` | `refactor` | `stage_result` | enum (`ALL_PASS`, `TARGET_FAIL`, `REGRESSION`, `ERROR`) | Outcome of `--stage refactor`. | Any non-`ALL_PASS` result means "refactor only under green" was violated. |
| `verification` | `refactor` | `refactor_performed` | boolean | Whether a refactor was actually attempted. | A persistently false rate suggests the refactor stage is being skipped rather than found unnecessary. |
| `run.finished` | `finish` | `stages_reached` | array of enum (`red`, `green`, `refactor`) | Which stages the cycle actually completed. | Reveals cycles that stop early — e.g. never reach `refactor` — without waiting for a `failure` outcome. |
| `run.finished` | `finish` | `final_stage_result` | enum (`FAIL_CORRECT`, `PASS_UNEXPECTED`, `ALL_PASS`, `TARGET_FAIL`, `REGRESSION`, `ERROR`) | The last recorded `stage_result`. | The terminal signal for whether the cycle actually finished green. |

An improvement agent should cross-tabulate `stage_result` per phase against
`task_category` (e.g. do `refactor` cycles skew toward `bug_fix`?), watch
`stages_reached` for cycles that systematically stop before `refactor`, and
track `mocks_used` drift against the anti-pattern guidance in
`references/testing-anti-patterns.md` to decide whether the Workflow section
of `SKILL.md` needs revision.
