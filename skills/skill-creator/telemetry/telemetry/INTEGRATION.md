# Integration guide: skill-creator

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

- `SKILL.md:9` — Before relying on CLI or skill-contract behavior, detect the local runtime and
- `SKILL.md:19` — 2. Inspect the existing skill and repository conventions before editing. For a
- `SKILL.md:24` — templates in `assets/` only when they are actually needed.
- `SKILL.md:26` — State the value hypothesis before testing. Build positive, negative, and
- `SKILL.md:28` — the contract's default corpus and repetition counts when practical; record
- `SKILL.md:31` — state with outcome rubrics fixed before results. Use
- `SKILL.md:32` — `codex exec` when available, capture exit status and final output, and use
- `SKILL.md:33` — `codex exec --json` only when runtime usage evidence is needed. Keep runs
- `SKILL.md:37` — Validated Performance and an overall `/100` only when repeated paired
- `SKILL.md:50` — - `scripts/package_skill.py`: creates a `.skill` archive after validation.
- `SKILL.md:72` — only when a documented Codex requirement and a test justify them.
- `SKILL.md:90` — Pause and report when the target runtime behavior is undocumented, a required
- `assets/eval_review.html:35` — .toggle .slider::before { content: ""; position: absolute; width: 18px; height: 18px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.2s; }
- `assets/eval_review.html:37` — .toggle input:checked + .slider::before { transform: translateX(20px); }
- `assets/eval_review.html:82` — if (group !== lastGroup) {

### Verification candidates

- `SKILL.md:13` — and validation behavior explicit.
- `SKILL.md:38` — evidence is sufficient. Static or deterministic validation leaves G5
- `SKILL.md:42` — and check for material regressions.
- `SKILL.md:43` — 8. Validate the package from the repository root. Check metadata, relative
- `SKILL.md:49` — - `scripts/quick_validate.py`: dependency-free metadata and package validation.
- `SKILL.md:50` — - `scripts/package_skill.py`: creates a `.skill` archive after validation.
- `SKILL.md:55` — - `eval-viewer/generate_review.py --static`: produces a reviewable HTML file
- `SKILL.md:72` — only when a documented Codex requirement and a test justify them.
- `SKILL.md:86` — unknown behavior, and validation evidence. Leave the source package untouched.
- `SKILL.md:91` — Codex command or schema is unavailable, a test needs external credentials, or
- `assets/eval_review.html:9` — <title>Eval Set Review - __SKILL_NAME_PLACEHOLDER__</title>
- `assets/eval_review.html:44` — <h1>Eval Set Review: <span id="skill-name">__SKILL_NAME_PLACEHOLDER__</span></h1>
- `assets/eval_review.html:49` — <button class="btn btn-export" onclick="exportEvalSet()">Export Eval Set</button>
- `assets/eval_review.html:60` — <tbody id="eval-body"></tbody>
- `assets/eval_review.html:71` — const tbody = document.getElementById('eval-body');

### Execution candidates

- `eval-viewer/generate_review.py:21` — import subprocess
- `eval-viewer/generate_review.py:276` — result = subprocess.run(
- `eval-viewer/generate_review.py:288` — except subprocess.TimeoutExpired:
- `eval-viewer/generate_review.py:354` — self.feedback_path.write_text(json.dumps(data, indent=2) + "\n")
- `eval-viewer/generate_review.py:419` — args.static.write_text(html)
- `eval-viewer/viewer.html:670` — const resp = await fetch("/api/feedback");
- `eval-viewer/viewer.html:698` — content.classList.remove("open");
- `eval-viewer/viewer.html:699` — document.getElementById("grades-arrow").classList.remove("open");
- `eval-viewer/viewer.html:755` — content.classList.remove("open");
- `eval-viewer/viewer.html:756` — document.getElementById("prev-outputs-arrow").classList.remove("open");
- `eval-viewer/viewer.html:840` — fetch("/api/feedback", {
- `eval-viewer/viewer.html:872` — fetch("/api/feedback", {
- `eval-viewer/viewer.html:894` — document.getElementById("done-overlay").classList.remove("visible");
- `eval-viewer/viewer.html:902` — setTimeout(() => toast.classList.remove("visible"), 2000);
- `eval-viewer/viewer.html:935` — document.querySelectorAll(".view-tab").forEach(t => t.classList.remove("active"));

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
