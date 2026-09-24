# Integration guide: systematic-debugging

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

- `LICENSE.txt:19` — LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
- `SKILL.md:3` — description: "Diagnose bugs, test or build failures, regressions, and unexpected behavior before a permanent fix; exclude planned features without a failure signal."
- `SKILL.md:11` — - **Trigger and exclusion:** Use before proposing a permanent fix for a bug, test failure, performance regression, build failure, or unexpected behavior; exclude planned feature work without a failure signal, routing it to feature-implementation.
- `SKILL.md:19` — - **References:** Resolve required references and scripts relative to this package; stop if a required bundled resource is absent.
- `SKILL.md:25` — Immediate containment may precede diagnosis only when needed to limit a
- `SKILL.md:37` — - Reproduce with the smallest reliable case. If intermittent, record frequency,
- `SKILL.md:41` — - When tests already fail, capture the pre-change baseline so introduced
- `SKILL.md:44` — If the failure cannot be reproduced or observed well enough to discriminate
- `SKILL.md:55` — Read [root-cause-tracing.md](../root-cause-tracing.md) when the bad state originates
- `SKILL.md:62` — the smallest reversible experiment that changes one meaningful variable. If
- `SKILL.md:66` — Repeated failed hypotheses do not prove that the architecture is wrong. After
- `SKILL.md:69` — whether broader architectural investigation is warranted. Ask before expanding
- `SKILL.md:74` — - Add the smallest durable regression check practical for the failure. When an
- `SKILL.md:78` — - Avoid unrelated refactors unless the root cause cannot be corrected safely
- `SKILL.md:79` — without them; surface that scope expansion before proceeding.

### Verification candidates

- `SKILL.md:3` — description: "Diagnose bugs, test or build failures, regressions, and unexpected behavior before a permanent fix; exclude planned features without a failure signal."
- `SKILL.md:11` — - **Trigger and exclusion:** Use before proposing a permanent fix for a bug, test failure, performance regression, build failure, or unexpected behavior; exclude planned feature work without a failure signal, routing it to feature-implementation.
- `SKILL.md:12` — - **Bounded workflow:** Establish the symptom and baseline, localize the fault, test one falsifiable hypothesis, implement the narrowest root-cause correction, and verify the original symptom plus relevant regressions.
- `SKILL.md:13` — - **Output:** Return the diagnosis, supporting evidence, change made or safe stop, validation results, and remaining uncertainty.
- `SKILL.md:39` — - Check relevant error output, stack traces, recent diffs, dependency/config
- `SKILL.md:59` — ### 3. Test a falsifiable hypothesis
- `SKILL.md:67` — three unsuccessful correction attempts, stop patching, re-check the
- `SKILL.md:74` — - Add the smallest durable regression check practical for the failure. When an
- `SKILL.md:75` — automated test is infeasible, define an observable manual or integration
- `SKILL.md:76` — check and explain the limitation.
- `SKILL.md:84` — For order-dependent test pollution, the bundled
- `SKILL.md:87` — ### 5. Verify and stop
- `SKILL.md:89` — Re-run the original reproduction and the new regression check, then run the
- `SKILL.md:90` — narrowest relevant surrounding validation capable of detecting collateral
- `SKILL.md:96` — - the regression check fails without the correction and passes with it, when

### Execution candidates

- `scripts/find_polluter.py:7` — import subprocess
- `scripts/find_polluter.py:31` — subprocess.run(["npm", "test", str(test_file)], stdout=subprocess.DEVNULL,
- `scripts/find_polluter.py:32` — stderr=subprocess.DEVNULL, check=False)

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
