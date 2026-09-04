# High-leverage skill evaluation contract

Use this contract to create, audit, revise, or decide whether to retain a Codex
skill. A skill should reduce uncertainty at consequential decision points while
preserving useful agent judgment elsewhere.

## Critical gates

- **G1 — Routing boundary:** metadata states the owned workflow, activation
  condition, and enough boundary information to distinguish neighbors.
- **G2 — Material decision value:** removing at least one instruction or
  mechanism creates a realistic risk of a materially worse decision.
- **G3 — Observable completion:** the workflow follows goal → action →
  observation → verification → completion and defines sufficient stop evidence.
- **G4 — Failure and autonomy controls:** predictable failures and consequential
  side effects have responses scaled to reversibility, blast radius, authority,
  external effect, privacy/security impact, and observability.
- **G5 — Empirical value:** repeated representative paired trials demonstrate
  material improvement over the same no-skill baseline without unacceptable
  regression.

G1–G4 are static-design gates. G5 requires runtime evidence; inspection,
deterministic validation, or one successful run cannot pass it.

## Design Readiness — 50 points

| Dimension | Points | Full-credit criterion |
|---|---:|---|
| Workflow ownership and routing | 8 | Concrete recurring workflow; what, when, and neighbor boundary are explicit. |
| Decision-changing information | 8 | Decision-Bearing Density ≥0.75. |
| Loading and scope architecture | 5 | Core contains mostly common-path material; conditional detail is deferred. |
| Decision envelope | 7 | Decision Coverage ≥0.90 with mandatory, prohibited, and judgment regions distinguished. |
| Deterministic mechanisms | 5 | Mechanical Coverage ≥0.90 after maintenance, portability, and security costs. |
| Evidence and completion | 7 | Action evidence, independent verification, success, baseline-failure separation, blockers, and stopping criteria are present. |
| Failure handling and autonomy | 6 | Failure Branch Coverage ≥0.90 with appropriate consequence controls. |
| Context efficiency | 4 | Core Relevance ≥0.80; report raw core size separately. |

Definitions:

- **Decision-Bearing Density** = decision-bearing substantive instructions /
  all substantive instructions. Routing, local knowledge, constraints,
  prohibitions, judgment rules, verification, failure handling, and reference
  loading count; generic advice does not.
- **Decision Coverage** = constrained + prohibited + intentionally delegated
  consequential decisions / consequential decisions identified.
- **Mechanical Coverage** = appropriately automated + justified linguistic
  repeated procedures / repeated mechanical procedures identified.
- **Failure Branch Coverage** = predictable failure modes with defined responses
  / predictable failure modes identified.
- **Core Relevance** = instructions needed in most invocations / substantive
  core instructions.

Report static results only as `Design Readiness: X/50 — UNVALIDATED`. Do not
extrapolate a static score to `/100`.

## Behavioral evaluation

Define the primary value hypothesis and outcome rubric before viewing results.
Unless cost or risk makes the default impractical, use at least:

- 20 positive routing prompts;
- 20 clear negative prompts;
- 10 neighboring or ambiguous prompts;
- 10 representative task scenarios;
- 5 realistic failure scenarios.

Run routing prompts at least three times each. Run task and failure scenarios at
least five times per condition, with and without the skill, from matched starting
states. If the default corpus is reduced, document the reason and classify the
result as insufficient for G5 unless equivalent statistical evidence exists.

Record at least two applicable efficiency measures: tokens, tool calls,
commands, wall time, or external operations. Preserve result metadata and
digests without secrets, private transcripts, or rollout bodies.

### Minimum routing targets

- precision ≥0.90;
- recall ≥0.90;
- neighbor false activation ≤0.15.

### Material-value test

G5 requires at least one predefined primary improvement:

- task success +10 percentage points; or
- relative error reduction ≥25%; or
- failure recovery +15 percentage points; or
- policy/safety violations reduced ≥50%; or
- efficiency improved ≥20% with task success falling no more than 2 points.

Critical violations must remain zero. Evaluate efficiency on successful runs;
doing less verification and failing more often is not an efficiency gain.

### Material regressions

Flag and adjudicate any of:

- task success down ≥5 points;
- routing precision or recall down ≥5 points;
- critical violations rising above zero;
- premature completion up ≥5 points;
- median execution cost up >25% without a predefined justification.

## Required scorecard

Report name, version or commit, evaluator, date, claimed workflow, value
hypothesis, corpus, repetitions, and matched-start method. Then report:

- G1–G5 as PASS, FAIL, or UNVALIDATED;
- Design Readiness `/50` by dimension;
- routing precision, recall, and neighbor false activation;
- task success and baseline uplift;
- relative error reduction;
- failure recovery and uplift;
- policy and critical violations;
- premature completion and unnecessary continuation;
- efficiency measures and ratios;
- Validated Performance `/50` only when evidence is sufficient;
- material-value result and regressions.

Finish with:

```text
Overall: X/100 or NOT REPORTABLE
Classification: FAIL / PASS / STRONG / EXCELLENT / EXCEPTIONAL / UNVALIDATED
Primary demonstrated value:
Largest remaining failure mode:
Material regression:
Next revision hypothesis:
```

Use `EXCEPTIONAL` only when repeated evaluation demonstrates material
improvement over the no-skill baseline.
