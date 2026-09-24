# Integration guide: last30days

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

- `AGENTS.md:13` — - `references/save-html-brief.md` - HTML export path when requested.
- `SKILL.md:10` — live source contract before treating research results as current.
- `SKILL.md:18` — - [HTML brief](../references/save-html-brief.md) - only when the user wants a shareable HTML artifact.
- `references/save-html-brief.md:3` — This reference file is loaded by the main `SKILL.md` when the user asked for an HTML brief (either explicitly via `--emit=html` / `--emit:html` / `--html`, or in natural language - "give me a shareable HTML brief", "for Slack", "for Notion", "export as HTML", etc.). The detection happens in `SKILL.md` so that the common no-HTML path stays short; the implementation lives here.
- `references/save-html-brief.md:7` — ## When to fire this flow
- `references/save-html-brief.md:9` — - After you have already emitted the full chat response: badge, "What I learned:" (or comparison title), bold-lead-in paragraphs with citations, KEY PATTERNS list, engine footer pass-through, invitation block.
- `references/save-html-brief.md:10` — - BEFORE the WAIT FOR USER'S RESPONSE pause.
- `references/save-html-brief.md:11` — - ONLY if the user asked. Do NOT save HTML when the user didn't ask for it.
- `references/save-html-brief.md:20` — #    footer in the temp file - the engine adds those when it renders the HTML.
- `references/save-html-brief.md:50` — # 3. Append ONE line to your already-emitted chat response, after the
- `references/save-html-brief.md:71` — Same flow when the topic is `X vs Y` (or `X vs Y vs Z`). The engine routes through `render_for_html_comparison` internally; you don't need to do anything special. The synthesis temp file should still contain the comparison-shaped synthesis you wrote in chat (`## Quick Verdict`, `## {Entity}` per entity, `## Head-to-Head` table, `## The Bottom Line`, `## The emerging stack` per LAW 4 comparison exception).
- `references/save-html-brief.md:75` — If the user runs `/last30days OpenClaw` normally, sees the synthesis in chat, and THEN says "save that as HTML" or "give me a shareable version" in a follow-up turn, do the same save flow on the synthesis you wrote in the previous turn. Do not re-research; the synthesis is already in the conversation history. Just write it to the temp file and call the engine with `--emit=html --synthesis-file`.
- `references/save-html-brief.md:79` — - Do NOT save HTML if the user didn't ask. The sparse mode (no synthesis) produces a thin file; not useful as a shareable.
- `references/save-html-brief.md:82` — - Do NOT silently overwrite an existing file without telling the user. If `$HTML_PATH` already exists from a prior run, the engine will pick a date-suffixed name (`{slug}-brief-YYYY-MM-DD.html`) automatically; just print whichever path the redirect produced.
- `references/save-html-brief.md:89` — - **Synthesis with images or non-ASCII**: emoji and Unicode pass through. Image tags pass through as raw HTML; the renderer doesn't transform them. If you didn't include images in chat, don't add them here.

### Verification candidates

- `SKILL.md:9` — Source and runtime behavior can change. Verify the bundled engine and each
- `VERIFICATION.md:8` — - Windows smoke check: `python scripts/last30days.py --help`.
- `scripts/AGENTS.md:11` — - `verify_v3.py` - validation helper.
- `scripts/AGENTS.md:22` — - Keep validation helpers close to the scripts they exercise.
- `scripts/evaluate_search_quality.py:329` — check=False,
- `scripts/evaluate_search_quality.py:337` — worktree_dir = Path(tempfile.mkdtemp(prefix="last30days-eval-"))
- `scripts/evaluate_search_quality.py:341` — check=True,
- `scripts/evaluate_search_quality.py:359` — check=False,
- `scripts/last30days.py:319` — Validation: top-level must be a dict; each value must be a dict. Unknown fields
- `scripts/last30days.py:897` — "cannot render a comparison. Re-run without --competitors or check the "
- `scripts/lib/bird_x.py:92` — """Check if vendored Bird search module is available.
- `scripts/lib/bird_x.py:103` — """Check if explicit X credentials are available.
- `scripts/lib/bird_x.py:119` — """Check if npm is available (kept for API compatibility).
- `scripts/lib/bird_x.py:305` — # Check if we got results
- `scripts/lib/bird_x.py:429` — # Check for errors

### Execution candidates

- `scripts/briefing.py:219` — with open(path, encoding="utf-8") as f:
- `scripts/briefing.py:228` — with open(path, "w", encoding="utf-8") as f:
- `scripts/evaluate_search_quality.py:10` — import subprocess
- `scripts/evaluate_search_quality.py:278` — cache_file.write_text(json.dumps(payload, indent=2))
- `scripts/evaluate_search_quality.py:322` — result = subprocess.run(
- `scripts/evaluate_search_quality.py:338` — subprocess.run(
- `scripts/evaluate_search_quality.py:356` — subprocess.run(
- `scripts/evaluate_search_quality.py:414` — (output_dir / "metrics.json").write_text(json.dumps(payload, indent=2))
- `scripts/evaluate_search_quality.py:438` — (output_dir / "summary.md").write_text("\n".join(lines) + "\n")
- `scripts/evaluate_search_quality.py:457` — metrics_path.write_text(json.dumps(payload, indent=2))
- `scripts/evaluate_search_quality.py:469` — summary_path.write_text("\n".join(lines).rstrip() + "\n")
- `scripts/last30days.py:125` — out_path.write_text(content, encoding="utf-8")
- `scripts/last30days.py:328` — plan_str = open(plan_str).read()
- `scripts/last30days.py:551` — (target / "last-run.json").write_text(json.dumps(payload, indent=2))
- `scripts/last30days.py:641` — plan_str = open(plan_str).read()

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
