# Codex Skills

This repository is a collection of repository-aware skills for Codex. Each skill is a focused `skills/<name>/SKILL.md` contract; some also include references, scripts, fixtures, or evaluation material. Execution behavior lives in the skill packs. The catalog and validator describe and check the collection without changing how skills run.

The machine-readable source of truth is [`skills/catalog.json`](skills/catalog.json). Validate it with:

```text
python scripts/validate_catalog.py
```

Consolidation and compatibility decisions are recorded in
[`docs/skill-consolidation.md`](docs/skill-consolidation.md). The canonical
precedence map is [`docs/skill-routing.md`](docs/skill-routing.md).

Evaluation maturity uses one four-level rubric in
[`docs/evaluation-rubric.md`](docs/evaluation-rubric.md); the canonical
skill-by-skill evidence is [`docs/evaluation-inventory.json`](docs/evaluation-inventory.json).
Manual prose scenarios are evidence for human review and are never described
as automated tests.

Run the complete offline repository validation with one command:

```text
python scripts/validate_repository.py
```

Run the deterministic Core benchmark with:

```text
python scripts/run_core_benchmark.py --deterministic-only
```

The validation layers are intentionally separate: repository validation,
deterministic routing fixtures, plugin-package validation, and optional live
Codex runtime evidence. Run the offline runtime harness with:

```text
python scripts/run_codex_evaluation.py --deterministic-only
```

The opt-in live probe uses a temporary `CODEX_HOME` and reports `PASS`, `FAIL`,
or `UNAVAILABLE` without touching user-level Codex state:

```text
python scripts/run_codex_evaluation.py --live
```

See [docs/control-plane/evaluation.md](docs/control-plane/evaluation.md) for
the evidence boundaries and generated-result policy.

This repository is also distributed as the root Codex plugin. The canonical
skill source remains `skills/`; validate the root manifest and Git-backed repo
marketplace with:

```text
python scripts/validate_plugin_package.py
```

The repo marketplace is for plugin distribution and points at the GitHub root
plugin. It is separate from `.agents/skills/`, which remains an inert
compatibility/discovery location, and from personal standalone installation
under `$HOME/.agents/skills` via `skill-installer`. Do not copy canonical
skills into either repository-local location.

Validate and run the reusable behavioral fixtures with:

```text
python scripts/run_core_evaluation.py --deterministic-only
```

See [docs/core-benchmark.md](docs/core-benchmark.md) for one-case, one-skill,
baseline, and full-harness commands. Explicit runtime results do not measure
implicit trigger-selection accuracy.

The gate is offline and dependency-free. Its tests, including three negative
fixtures, run with:

```text
python -m unittest discover -s tests -v
```

## How to read this repository

Each skill is a `SKILL.md` contract: it tells Codex when to invoke the skill,
what process to follow, and what to deliver. That guidance is separate from
the evidence around it:

- **Deterministic helpers** are scripts that can check structure, plans, or
  other repeatable invariants.
- **Validation** is repository-level checking such as catalog integrity,
  trigger declarations, Markdown links, syntax, and whitespace.
- **Behavioral evaluation** is the skill's `VERIFICATION.md`, evaluation cases,
  or tests that assess whether the guidance produces the intended result.

Not every skill has every layer. The canonical inventory records each skill's
implementation depth and evaluation level; `prompt-only` is guidance without a
bundled executable artifact, while `script-backed`, `evaluated`, and `tested`
indicate progressively richer supporting evidence. These labels describe
available validation, not a guarantee of output quality.

## Front-door set

Start with one lifecycle-oriented domain, then follow its default owner or
choose a named specialist. Ownership is maintained once in the machine-
readable catalog; precedence remains canonical in the routing guide.

| Domain | Default owner | Use for |
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

The complete 50-skill catalog follows below. Explicit specialist nouns still
override broad lifecycle routing: PR review, TDD, vertical slices, worktrees,
skill audits, Codex audits, Context7 skill generation, and plugin packaging.

Use `systematic-debugging` when something fails, `acceptance-criteria` when
behavior needs an observable contract, and `read-the-damn-docs` when a
third-party technology is involved. Use the [canonical routing
guide](docs/skill-routing.md) when adjacent skills overlap.

## Routing rules

Route to the narrowest skill whose primary deliverable matches the request.
Explicit constraints and deliverables take precedence: PR or merge review
beats generic review, TDD beats standalone QA, a cross-layer slice beats
ordinary implementation, and a skill-package or Codex-control-plane audit
beats a broad repository audit. Compose later skills only when the request
explicitly contains both scopes. The legacy `grill-me` entry is retained only
for explicit `/grill-me` compatibility; new stress-test requests use
`grilling`.

## Validation command center

| Check | Command |
|---|---|
| Repository quality gate | `python scripts/validate_repository.py` |
| Full automated tests | `python -m unittest discover -s tests -v` |
| Deterministic Core benchmark | `python scripts/run_core_benchmark.py --deterministic-only` |
| Root plugin package | `python scripts/validate_plugin_package.py` |
| Skill inventory count and coverage | `python scripts/validate_skill_inventory.py` |

The quality gate enforces catalog integrity, inventory coverage, Core contract
dimensions, evaluation evidence, Python/JSON validity, tracked-artifact
hygiene, and committed whitespace checks. The benchmark validates positive,
negative, and ambiguous cases for every Core skill; implicit runtime selection
is intentionally reported as unavailable until telemetry exists.

## Maturity and provenance

Maturity is a routing classification, not a quality ranking. The lists below
are maintained in [`docs/skill-inventory.md`](docs/skill-inventory.md), which
is the canonical human-readable inventory; do not infer a different class
from the table in this README.

| Classification | Meaning | Count |
|---|---|---:|
| **Core** | Foundational lifecycle or repository workflow | 23 |
| **Specialized** | Focused domain, artifact, or operating context | 26 |
| **Experimental** | Explicitly experimental skills | 0 |
| **Vendored/Adapted** | Compatibility or imported form; canonical label: `Vendored-or-Adapted` | 1 |

The inventory records per-skill provenance as `original`, `adapted`,
`vendored`, or `unknown`, with repository links where evidence exists. The
repository is licensed under MIT; see [`LICENSE`](LICENSE). Per-skill status
belongs in the canonical inventory, not in duplicated README claims.

The post-consolidation repository retains all 50 skill entrypoints. The only
compatibility alias is `grill-me` → `grilling`; no skill is deprecated or
removed. The canonical human-readable inventory is [`docs/skill-inventory.md`](docs/skill-inventory.md), and it must contain each top-level
`skills/` directory exactly once.

## Software-delivery lifecycle

The main delivery path is:

```text
discovery → scope/specification → architecture/design → implementation → testing/QA → review → maintenance
```

- Discovery turns uncertainty into a problem, user, evidence, and validation plan (`product-discovery`, `mvp-scope`, `brainstorming-ux-features`).
- Specification turns intent into behavior and acceptance criteria (`product-spec`, `acceptance-criteria`, `writing-plans`).
- Architecture and design cover system boundaries, APIs, data, integrations, stacks, and visual systems (`architecture`, `api-design`, `data-modeling`, `integration-engineering`, `design-md-ideator`).
- Implementation ships a focused vertical slice with the existing repository tooling (`feature-implementation`, `vertical-slice`, `using-git-worktrees`).
- Testing and QA establish evidence, diagnose failures, and cover security (`test-driven-development`, `testing-qa`, `systematic-debugging`, `security-best-practices`).
- Review checks diffs and release risk (`review-agent`, `pr-review`, `visual-recap`).
- Maintenance keeps history, documentation, governance, and Git state healthy (`changelog-updater`, `generating-readmes`, `maintaining-repository-hygiene`, `git-workflow`).

## Meta-skills

Meta-skills improve the agent environment or the skill collection itself rather than implementing product behavior. They include context and intent management (`context-doctor`, `intent-layer`), skill authoring and distribution (`skill-creator`, `skill-auditor`, `context7-skill-wizard`, `skill-installer`, `plugin-creator`), orchestration and limits (`efficient-frontier`, `stay-within-limits`), and documentation/tooling boundaries (`read-the-damn-docs`, `openai-docs`).

## Capability map and catalog

The table below is a concise capability map grouped by lifecycle stage. Names,
descriptions, and capability levels are grounded in `skills/catalog.json` and
cross-referenced with the canonical inventory. Capability levels mean:
`prompt-only` has no bundled executable artifact, `script-backed` has reusable
scripts, `evaluated` has verification/evaluation artifacts, and `tested` has
executable tests or self-tests.

| Skill | Category | Lifecycle | Level | Description |
|---|---|---|---|---|
| acceptance-criteria | product | specification | prompt-only | Observable pass/fail acceptance criteria |
| api-design | architecture | architecture | prompt-only | API contracts and boundary design |
| architecture | architecture | architecture | prompt-only | Architecture decisions and system designs |
| brainstorming-ux-features | product | discovery | evaluated | Evidence-backed UX feature discovery |
| changelog-updater | maintenance | maintenance | tested | User-facing changelog reconstruction and updates |
| context-doctor | meta | meta | evaluated | Codex context and control-plane audit |
| context7-skill-wizard | meta | meta | evaluated | Documentation-grounded skill generation |
| data-modeling | architecture | architecture | prompt-only | Durable data model design and review |
| database-migrations | architecture | implementation | prompt-only | Safe schema changes and backfills |
| design-md-ideator | design | specification | tested | DESIGN.md design-system ideation and validation |
| efficient-frontier | meta | meta | evaluated | Delegated frontier-model orchestration |
| feature-implementation | delivery | implementation | prompt-only | Smallest verified feature slice |
| generate-codeowners | governance | maintenance | tested | Evidence-backed CODEOWNERS generation and audit |
| generating-readmes | documentation | maintenance | evaluated | Grounded repository README authoring |
| git-commit | delivery | maintenance | prompt-only | Git commit and Conventional Commit workflow |
| git-workflow | delivery | maintenance | prompt-only | Safe Git operations and recovery |
| github-issue-to-pr | delivery | implementation | evaluated | Issue-to-PR delivery workflow |
| grill-me | product | discovery | prompt-only | Compatibility alias for explicit `/grill-me` invocations |
| grilling | product | discovery | evaluated | One-question-at-a-time design stress test |
| imagegen | design | implementation | evaluated | Raster image generation and editing |
| improve | governance | review | script-backed | Evidence-backed repository improvement audits |
| integration-engineering | architecture | implementation | prompt-only | External API and service integrations |
| intent-layer | meta | meta | evaluated | Hierarchical AGENTS.md context setup |
| last30days | research | discovery | script-backed | Current public sentiment and trend research |
| maintaining-repository-hygiene | governance | maintenance | tested | Repository governance and hygiene audit |
| mvp-scope | product | discovery | prompt-only | MVP must-have/later/won't-build decisions |
| openai-docs | research | cross-cutting | evaluated | Authoritative OpenAI product documentation |
| plugin-creator | meta | meta | evaluated | Codex plugin scaffolding and validation |
| pr-review | quality | review | evaluated | Defect-first PR and diff review |
| product-discovery | product | discovery | prompt-only | Problem, user, assumptions, and validation |
| product-spec | product | specification | prompt-only | Implementable product behavior specification |
| read-the-damn-docs | research | cross-cutting | evaluated | Current authoritative third-party documentation |
| review-agent | quality | review | evaluated | Read-only defect-first change review |
| security-best-practices | quality | review | prompt-only | Secure-by-default web-stack guidance |
| simplification-cascades | quality | review | script-backed | Complexity-reducing unifying insights |
| skill-auditor | meta | meta | script-backed | Skill-pack and workflow audit |
| skill-creator | meta | meta | evaluated | Skill authoring and evaluation tooling |
| skill-installer | meta | meta | script-backed | Skill installation from curated/GitHub sources |
| stack-detection | architecture | architecture | evaluated | Desktop client stack classification |
| stay-within-limits | meta | meta | evaluated | Usage-limit-aware work orchestration |
| systematic-debugging | quality | testing | script-backed | Root-cause debugging workflow |
| tailwind-design-system | design | implementation | evaluated | Tailwind tokens, variants, and accessibility |
| taste-engine | design | specification | prompt-only | Opt-in design preference application |
| test-driven-development | quality | testing | script-backed | Red-green-refactor development cycle |
| testing-qa | quality | testing | prompt-only | Proportionate verification and QA |
| using-git-worktrees | delivery | implementation | script-backed | Isolated Git worktree setup and verification |
| vertical-slice | delivery | implementation | prompt-only | End-to-end user-visible slice delivery |
| visual-plan | planning | specification | evaluated | Visual implementation plans |
| visual-recap | quality | review | evaluated | Visual diff and PR recaps |
| writing-plans | planning | specification | script-backed | TDD-first implementation plans |

The validator intentionally checks only catalog integrity: exact skill coverage, frontmatter names, references, paths, artifacts, and allowed capability labels. It does not execute skill behavior. Some skills therefore have richer automated validation than others; a green catalog check is not a behavioral benchmark.

## Provenance, licensing, and support boundaries

`SKILL.md` files are the executable guidance surface for Codex. Scripts,
fixtures, verification notes, and tests are supporting artifacts and may cover
only some skills. The catalog and inventory describe those boundaries; they do
not certify that every skill has equivalent evaluation depth.

The policy is deliberately evidence-first:

- `original` means repository evidence establishes first-party authorship.
- `adapted` means repository evidence identifies a modified or compatibility form.
- `vendored` means third-party code or assets are carried in the repository.
- `unknown` means authorship or origin is not established; it is not a guess.

Contribution workflow details are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

The root project license is MIT ([`LICENSE`](LICENSE)). For vulnerability
reporting, see [`SECURITY.md`](SECURITY.md). Vendored material is
The intentional
`last30days` vendored runtime is documented in
[`skills/last30days/scripts/lib/vendor/README.md`](skills/last30days/scripts/lib/vendor/README.md).
Vendored material is
kept under explicitly named `vendor/` paths where practical and retains its
own notices. Review those notices and any linked source before redistribution;
no existing copyright or license notice is replaced by the root policy.
