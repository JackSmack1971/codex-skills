# Skill Routing Guide

This is the canonical precedence guide for semantically adjacent skills. Route
to the narrowest skill whose primary deliverable matches the request. A skill
may delegate to a later row when the request explicitly contains both scopes;
delegation does not change the primary route.

The overlap and compatibility decisions behind these boundaries are documented
in [`skill-consolidation.md`](skill-consolidation.md).

## Front-door set

Choose a lifecycle domain first when a request does not name a specialist.
Ownership is declared once in [`skills/catalog.json`](../skills/catalog.json),
where every skill belongs to exactly one domain; the owner is the default
entrypoint. The precedence rules below remain canonical for explicit nouns.

| Domain | Default owner | Scope |
|---|---|---|
| Discover | `product-discovery` | Problems, users, evidence, and scope |
| Specify | `product-spec` | Behavior, acceptance criteria, and plans |
| Design | `architecture` | System, API, data, integration, and visual boundaries |
| Build | `feature-implementation` | Product implementation |
| Verify | `testing-qa` | Tests, diagnosis, and security |
| Review | `review-agent` | Change and merge-risk review |
| Release | `github-issue-to-pr` | Isolation, commits, and pull requests |
| Maintain | `maintaining-repository-hygiene` | History, docs, and governance |
| Improve | `improve` | Evidence-backed repository improvement |
| Extend skills | `skill-creator` | Skill authoring and distribution |
| Configure Codex | `context-doctor` | Codex context and control-plane behavior |
| Orchestrate | `efficient-frontier` | Delegated work and usage limits |

Front doors are navigation only. Named specialists remain directly invokable.

## Review

| Skill | Use when | Do not use when | Delegates/composes with | Precedence |
|---|---|---|---|---|
| `review-agent` | A delegated, read-only defect review targets uncommitted changes, a commit, or a diff. | The request names a pull request or proposed merge, or asks to post GitHub review output. | `systematic-debugging` for a reproduced defect; `testing-qa` for separate QA. | Wins for delegated/read-only defect review without PR/merge output. |
| `pr-review` | Reviewing a pull request, proposed merge, or GitHub-hosted branch with merge-risk findings or review comments. | The request is a generic delegated code-change review with no PR/merge deliverable. | `testing-qa` for verification; `git-workflow` for repository state. | Wins whenever PR, proposed merge, merge-risk, or GitHub review output is explicit. |

## Feature delivery and verification

| Skill | Use when | Do not use when | Delegates/composes with | Precedence |
|---|---|---|---|---|
| `vertical-slice` | The central problem is tracing one user action end to end across UI, service/API, persistence, and verification. | A feature can be implemented without cross-layer slicing, or the request is only a test workflow. | `feature-implementation` for code changes; `data-modeling` for durable model design; `testing-qa` for broader QA. | Wins when end-to-end cross-layer scope is explicit. |
| `test-driven-development` | The requested work explicitly requires a red-green-refactor TDD cycle gated by local results. | QA is requested without TDD, or implementation is requested without a test-first constraint. | `feature-implementation` or `vertical-slice` for the delivered change. | Wins for an explicit TDD constraint. |
| `testing-qa` | Choosing or running proportionate QA for an existing change, without requiring TDD. | The workflow explicitly requires red-green-refactor TDD. | `pr-review` for PR review; `systematic-debugging` when a check exposes an unexpected failure. | Wins for standalone QA verification. |
| `feature-implementation` | Implementing specified product behavior as the smallest verified change. | The request is primarily a cross-layer slice plan, explicit TDD cycle, or QA-only request. | `vertical-slice`, `test-driven-development`, or `testing-qa` when those constraints are explicit. | Default implementation route; narrower constraints override it. |

## Repository and skill audits

| Skill | Use when | Do not use when | Delegates/composes with | Precedence |
|---|---|---|---|---|
| `skill-auditor` | Auditing skill packages, SKILL.md metadata, or multi-skill handoffs for routing, drift, safety, or validation. | The audit is only about Codex runtime/control-plane loading, or general repository improvement without skill artifacts. | `skill-creator` for authorized remediation; `context-doctor` for Codex control-plane evidence. | Wins when skill packages or skill routing are the audited artifact. |
| `context-doctor` | Auditing Codex context loading, AGENTS.md, config, hooks, MCP, or model/control-plane settings. | The target is a skill package rather than Codex runtime configuration. | `skill-auditor` for skill-package findings; `openai-docs` for official product behavior. | Wins when Codex control-plane configuration or loading is explicit. |
| `improve` | Auditing a general repository for evidence-backed improvement opportunities and writing plan-only handoffs. | The target is a skill package or Codex control plane, or implementation is requested. | `skill-auditor` or `context-doctor` for narrower audits; `feature-implementation` for execution handoff. | Broad default; narrower audit targets override it. |

## Git operations and issue delivery

| Skill | Use when | Do not use when | Delegates/composes with | Precedence |
|---|---|---|---|---|
| `github-issue-to-pr` | Converting an open GitHub issue into a focused PR with planning, state tracking, and isolation. | Only a local Git operation, commit, or worktree is requested. | `using-git-worktrees`, `git-workflow`, `feature-implementation`, and `pr-review`. | Wins for the complete issue-to-PR lifecycle. |
| `using-git-worktrees` | Creating or verifying an isolated worktree for parallel or branch-isolated work. | Isolation is not requested or the task is the complete issue-to-PR lifecycle. | `git-workflow`; commonly composed by `github-issue-to-pr`. | Wins when worktree isolation is the requested deliverable. |
| `git-commit` | Creating a commit or Conventional Commit message when explicitly requested. | The request is broader Git state/recovery or a complete issue-to-PR workflow. | `git-workflow` for repository state; `github-issue-to-pr` for issue delivery. | Wins for an explicit commit request, unless issue-to-PR owns the lifecycle. |
| `git-workflow` | A Git operation such as status, branch, sync, stage, merge, rebase, push, or recovery. | The request is specifically only a commit message/commit or isolated worktree creation. | `git-commit`, `using-git-worktrees`, or `github-issue-to-pr`. | Broad fallback; narrower requested deliverables override it. |

## Skill, technology, and plugin authoring

| Skill | Use when | Do not use when | Delegates/composes with | Precedence |
|---|---|---|---|---|
| `context7-skill-wizard` | Building a focused skill from current Context7 docs for a named library or framework. | General skill authoring, migration, metadata, or evaluation without a named technology. | `skill-creator` for general authoring and `read-the-damn-docs` for source grounding. | Wins for named-library/framework skill generation using Context7. |
| `skill-creator` | General skill authoring, migration, improvement, evaluation, metadata, or description work. | A named-library/framework Context7 generation request, or plugin scaffolding. | `skill-auditor` for audit findings; `plugin-creator` for plugin packaging. | Wins for skill work without the Context7-wizard trigger. |
| `plugin-creator` | Creating or updating a Codex plugin manifest, optional plugin structure, or marketplace metadata. | Editing a standalone SKILL.md without plugin packaging. | `skill-creator` for bundled skills; `skill-installer` for installation. | Wins whenever plugin, manifest, or marketplace packaging is explicit. |

## Precedence summary

Explicit artifact and deliverable nouns beat broad verbs: PR/merge beats
review, TDD beats testing, cross-layer slice beats generic implementation,
skill-package or Codex-control-plane target beats broad audit, issue-to-PR
beats individual Git steps, and plugin packaging beats standalone skill
authoring. If two scopes are explicitly requested, route to the lifecycle
owner and compose the narrower skill as listed above.
