# Empirical skill-value campaign

Status: `BLOCKED_RUNTIME_UNAVAILABLE` as of 2026-09-04. The repository's
deterministic suite passes, but the execution environment used for this
revision has no `codex` executable. No runtime result or G5 claim was produced.

The governing contract is
[high-leverage-skill-evaluation.md](high-leverage-skill-evaluation.md). Matched
no-skill and explicit-skill trials must use the same starting state and a rubric
fixed before results are viewed. Metadata-only reports belong in
`evals/codex/results/`; response bodies, transcripts, reasoning, secrets, and
private runtime data must not be retained.

## Revision order

1. Expand routing coverage to at least 20 positive, 20 negative, and 10
   neighboring prompts per evaluated skill; repeat each routing prompt three
   times.
2. Add at least 10 representative task scenarios and 5 realistic failure
   scenarios per evaluated skill; run five matched trials per condition.
3. Evaluate high-consequence skills first: `systematic-debugging`,
   `git-workflow`, `database-migrations`, and `stay-within-limits`.
4. Evaluate the prove-or-compress cohort next: `architecture`, `api-design`,
   `data-modeling`, `acceptance-criteria`, `product-discovery`, `product-spec`,
   `feature-implementation`, `testing-qa`, `vertical-slice`, `mvp-scope`, and
   `efficient-frontier`.
5. Record routing, task success, failure recovery, forbidden and critical
   violations, premature completion, command/tool cost, response cost, and wall
   time. Apply predefined material-value and regression thresholds.
6. Retain, compress, merge, or delete only after sufficient evidence. An
   exploratory signal or unavailable runtime authorizes no pruning.

## Runtime entry point

After installing and authenticating Codex in a dedicated evaluation home, run a
small harness check first:

```text
python scripts/run_core_evaluation.py --skill systematic-debugging --paired --runs 2 --output evals/codex/results/systematic-debugging-smoke.json
```

This existing six-case smoke corpus produces only an exploratory signal. Do not
promote it to G5. Expand the corpus and run the full repetitions above before a
retention decision.

## Current pruning decision

`NO_CHANGE — INSUFFICIENT_RUNTIME_EVIDENCE`. The earlier rewrite compressed
`systematic-debugging` by removing repetition and unsupported claims, but no
skill is deleted or merged in this stage.
