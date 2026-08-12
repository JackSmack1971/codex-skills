# Skill consolidation decisions

This is the decision record for reducing routing ambiguity without merging
skills whose deliverables or safety boundaries differ. Evidence was collected
from the frontmatter descriptions, `skills/catalog.json`,
`tests/skill-routing-cases.json`, the per-skill evaluation cases, and:

```text
python scripts/check_trigger_overlap.py
python scripts/validate_catalog.py
python scripts/validate_skill_inventory.py
```

The routing-boundary auditor combines lexical and explainable semantic
candidate detection, reciprocal pair checks, distinctive-term analysis, and
validated routing cases. It remains an offline metadata contract and does not
claim to measure implicit model routing. No skill directory is removed in this
revision. Use `--report-json` for inspectable candidate evidence or
`--generate-cases PATH` to write deterministic, human-reviewable case proposals
without modifying the canonical fixture.

## Decision summary

| Surface | Decision | Behavioral distinction | Compatibility impact and migration | Evidence |
|---|---|---|---|---|
| `review-agent` / `pr-review` | Retain separate | `review-agent` is delegated, read-only local change review; `pr-review` is PR/proposed-merge review with merge-risk output and optional GitHub submission. | No migration. Existing routes and both paths remain valid. | Frontmatter exclusions, routing cases `review-agent-*`/`pr-review-*`, and both evaluation case files. |
| `feature-implementation` / `vertical-slice` / `test-driven-development` / `testing-qa` | Retain separate | Ordinary implementation, cross-layer user-action tracing, explicit red-green-refactor TDD, and standalone proportionate QA are different primary deliverables. | No migration. Compose the narrower skill only when its constraint is explicit. | Frontmatter precedence rules, routing cases for all four skills, and each evaluation case file. |
| `improve` / `skill-auditor` / `context-doctor` | Retain separate | Broad repository improvement planning, skill-package/workflow auditing, and Codex control-plane auditing have different targets and authority boundaries. | No migration. Route by audited artifact; preserve read-only control-plane behavior. | Frontmatter exclusions, routing cases for all three skills, and the auditor/doctor evaluation cases. |
| Git helpers | Retain separate | `git-workflow` owns broad Git operations; `git-commit` owns commit-only requests; `using-git-worktrees` owns isolation; `github-issue-to-pr` owns the issue lifecycle. | No migration. Existing paths remain; the lifecycle skill composes the narrower helpers. | Frontmatter precedence rules, routing cases for all four skills, and Git evaluation case files. |
| `grill-me` / `grilling` | Retain compatibility alias | `grilling` is canonical; `grill-me` preserves explicit legacy `/grill-me` invocations. | Backward compatible. New invocations use `grilling`; old `/grill-me` calls continue to resolve. | `skills/catalog.json` `alias_of`, both frontmatter descriptions, routing cases, and inventory classification. |

## Generic contract consolidation

Core skills share one safety and evidence baseline in
[`core-quality-contract.md`](core-quality-contract.md). The skill-specific
trigger, exclusion, workflow, and deliverable remain in each `SKILL.md`; the
shared baseline is not a second routing surface. This preserves behavior while
avoiding future drift in repeated generic instructions.

## Inventory impact

```text
top-level skills before: 50
top-level skills after:  50
removed: none
deprecated: none
new aliases: none
retained compatibility aliases: grill-me -> grilling
```

The unchanged count is intentional: the evidence shows distinct workflows,
not redundant skill entrypoints. A future merge requires new routing and
evaluation evidence plus an explicit compatibility path for the old name.
