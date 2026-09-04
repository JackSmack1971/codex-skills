# Post-revision skill quality audit — 2026-09-04

Commit under review: the head of `codex/revision-ordered-skill-quality` after
the ordered remediation series. Governing contract:
[high-leverage-skill-evaluation.md](high-leverage-skill-evaluation.md).

## Executive result

**Design Readiness: 42/50 — UNVALIDATED**

| Gate | Result | Evidence |
|---|---|---|
| G1 routing boundary | PASS | Runtime frontmatter is canonical; catalog duplication is rejected; aggregate discovery and overlap fixtures validate. |
| G2 material decision value | PASS, portfolio caveat | High-consequence workflows contain decision-bearing controls; the generic prove-or-compress cohort still requires runtime evidence. |
| G3 observable completion | PASS | Core contracts and deterministic validators require outputs, verification, stopping behavior, and failure separation. |
| G4 failure and autonomy controls | PASS | Consequential Git, migration, hygiene, review, and debugging paths retain explicit safety and stop boundaries. |
| G5 empirical value | UNVALIDATED | The local runtime is unavailable and the existing six-case-per-skill corpus is exploratory, not the required repeated matched campaign. |

Validated Performance: `NOT YET TESTED`

Overall: `NOT REPORTABLE`

Classification: `UNVALIDATED`

## Design Readiness

| Dimension | Max | Score | Remaining deduction |
|---|---:|---:|---|
| Workflow ownership and routing | 8 | 8 | — |
| Decision-changing information | 8 | 6 | Generic front-door skills have not proved marginal value. |
| Loading and scope architecture | 5 | 4 | `imagegen` and repository hygiene still carry substantial conditional core detail. |
| Decision envelope | 7 | 6 | Some lower-consequence skills still rely on broad judgment rules. |
| Deterministic mechanisms | 5 | 5 | Evidence labels now match executed commands and drift checks cover shared contracts. |
| Evidence and completion | 7 | 5 | Runtime outcome evidence remains unavailable. |
| Failure handling and autonomy | 6 | 5 | Portfolio-wide failure-case trials remain outstanding. |
| Context efficiency | 4 | 3 | The debugging core was compressed, but the wider context-economics pass remains open. |
| **Total** | **50** | **42** | **UNVALIDATED** |

## Ordered remediation result

1. Correctness and control-plane defects: complete. First-party Codex usage
   signals, official OpenAI documentation routing, debugging claims and
   provenance, installer overwrite semantics, and the stale internal skill
   reference were corrected.
2. Evidence semantics: complete. Deterministic-only commands can no longer be
   labeled automated behavioral evidence.
3. Runtime routing metadata: complete. `SKILL.md` frontmatter is canonical and
   the catalog may not duplicate it.
4. Meta-skills: complete. `skill-creator` and `skill-auditor` share and enforce
   the G1–G5 contract.
5. Empirical campaign: blocked by unavailable Codex runtime; the deterministic
   harness passed and the runtime state was recorded as unavailable.
6. Evidence-based pruning: correctly deferred. Current evidence authorizes no
   deletion or merge.
7. Re-score: complete at 42/50 Design Readiness; G5 remains unvalidated.

## Remaining work

- Execute [the empirical campaign](empirical-campaign.md) in an authenticated
  Codex environment after expanding its corpus to the governing minimums.
- Resolve or document the 47 remaining `unknown` provenance records.
- Use matched evidence to retain, compress, merge, or delete the generic
  prove-or-compress cohort.
- Revisit `imagegen` and repository-hygiene core relevance after behavioral
  evidence identifies which conditional instructions affect outcomes.

Primary demonstrated value: structural and semantic validation now prevents
three prior classes of overclaim—false behavioral labels, routing-description
drift, and smoke-scale pruning decisions.

Largest remaining failure mode: absence of repeated matched runtime results.

Material regression: none detected by the deterministic repository, routing,
delivery, and unit-test gates.

Next revision hypothesis: a full paired campaign will distinguish genuinely
decision-changing generic skills from instructions that should be compressed or
removed.
