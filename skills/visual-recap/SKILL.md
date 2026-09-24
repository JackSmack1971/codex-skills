---
name: visual-recap
description: "Turn PRs, branches, commits, or diffs into interactive visual recaps with diagrams and focused review notes."

---

# Visual Recap

Use `/visual-recap` for a non-trivial PR, branch, commit, or diff that needs a
reviewable Agent-Native Plan. Derive the recap from the complete work unit,
not from a summary alone.

## Required behavior

- Inventory meaningful UI states, routes, roles, files, schemas, APIs, and
  shared abstractions before authoring.
- Always publish a structured plan: UI headline when relevant, outcome
  narrative, changed-file tree, and focused key-change evidence.
- Use wireframes for rendered UI changes; use the correct surface and show
  entry, interaction, destination, and permission/error states as needed.
- Read the live block catalog before writing blocks; use exact runtime tags and
  required fields.
- Build `data-model`, `api-endpoint`, `file-tree`, `diff`, and `annotated-code`
  blocks mechanically from the real diff. Use valid single-value JSON examples.
- Keep key diffs focused, summarized, annotated, and grouped in horizontal
  tabs; omit only redundant boilerplate, not review-critical evidence.
- Keep private recaps gated, use returned absolute URLs, redact secrets, and
  route reviewer annotations back into the plan/code loop.

## Workflow and stop conditions

Inventory → read block schema and wireframe guidance → author grounded recap →
self-review → validate/render → publish. Stop when a required diff, visual
fact, connector/schema check, or safe redaction is unavailable; never invent
implementation details.

Detailed mapping, budgets, publication, safety, grounding, and review-loop
guidance: [entrypoint guidance](references/entrypoint-guidance.md). Read the
[wireframe reference](references/wireframe.md) before any wireframe.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before "Inventory", start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<pr|branch|commit|diff>" --invocation explicit)
   ```
2. After "Inventory" (meaningful UI states, routes, roles, files, schemas,
   APIs, shared abstractions), record the inventory decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase inventory \
     --evidence-json '{"change_surfaces":["<subset of ui_states,routes,roles,files,schemas,apis,shared_abstractions>"],"key_change_tabs_count":<N>}'
   ```
3. After "author grounded recap" (building `data-model`, `api-endpoint`,
   `file-tree`, `diff`, and `annotated-code` blocks mechanically from the
   diff), record the authoring operation:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event operation --phase author \
     --evidence-json '{"block_types_used":["<subset of data-model,api-endpoint,file-tree,diff,annotated-code>"],"wireframe_used":<true|false>,"wireframe_variant":"<before_after|after_only|sequence|none>"}'
   ```
4. After "self-review → validate/render", record the validation check:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase validate --outcome <success|failure> \
     --evidence-json '{"block_catalog_validated":<true|false>,"secrets_redacted":<true|false>,"tabs_within_budget":<true|false>}'
   ```
5. Before "publish", close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"publish_mode":"<hosted|local_files>","block_types_used":["<subset of data-model,api-endpoint,file-tree,diff,annotated-code>"],"key_change_tabs_count":<N>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g. `missing_diff`,
   `connector_unavailable`, `secret_unredactable`) when the workflow stopped
   under a stop condition instead of publishing a recap.

If a reviewer's routed-back annotation later disputes this run's grounding
or flags a missed change, record it so recap quality is visible without
re-running the skill:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"correction":"<annotation_disputes_grounding|missing_change_flagged|wireframe_state_wrong>"}'
```
