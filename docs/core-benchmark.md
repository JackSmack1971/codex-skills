# Core skill benchmark

The benchmark manifest is [`benchmarks/core/manifest.json`](../benchmarks/core/manifest.json). It contains one representative task and positive, negative, and ambiguous trigger cases for each of the 23 Core skills.

Run the baseline (deterministic checks plus one explicit model-backed sample when `codex` is installed):

```text
python scripts/run_core_benchmark.py --output benchmarks/core/baseline.json
```

Use `--deterministic-only` for an offline run, or `--runs 3` to repeat the model-backed sample. The report records the manifest, UTC timestamp, task identity, run count, exit code, response digest/size, pass criteria, and uncertainty. It deliberately omits response bodies, transcripts, and secrets.

Audit adjacent-skill routing boundaries separately with
`python scripts/check_trigger_overlap.py`. The auditor discovers lexical and
explainable semantic candidates, validates reciprocal boundary cases, and
reports distinctive terms. Its fixture-backed result is deterministic evidence,
not an implicit-selection accuracy measurement.

Measurement modes are separate. Explicit cases name `$skill` in the prompt. Implicit selection is currently **unavailable and unreported** because the local Codex CLI does not expose selected-skill telemetry; explicit results must not be read as implicit trigger accuracy. Model responses are human-review material, not fake objective scores.
# Core benchmark

The existing deterministic benchmark validates the Core-skill manifest and its
positive, negative, and ambiguous routing fixtures. It does not claim implicit
skill-selection accuracy.

## Behavioral harness

The reusable behavioral contract is [benchmarks/core/behavioral-schema.json](../benchmarks/core/behavioral-schema.json), with offline fixtures in
[benchmarks/core/behavioral-cases.json](../benchmarks/core/behavioral-cases.json).
It supports required headings/text/files, forbidden text, stop behavior, and
validator exit-code assertions.

Run the deterministic schema/fixture validation:

```text
python scripts/run_core_evaluation.py --deterministic-only
```

Run one case through Codex when available:

```text
python scripts/run_core_evaluation.py --case-id acceptance-criteria-positive
```

Run one Core skill's cases:

```text
python scripts/run_core_evaluation.py --skill acceptance-criteria
```

Run a baseline without deliberately invoking the target skill:

```text
python scripts/run_core_evaluation.py --case-id acceptance-criteria-positive --baseline
```

Runtime reports contain only exit codes, response size/hash, assertion results,
and availability metadata. Response bodies and transcripts are never written.
Explicit runs are labeled `explicit`; they are not implicit trigger-selection
measurements. If Codex is unavailable, deterministic validation still exits 0
and runtime entries report `unavailable`.

The separate plugin/runtime distribution harness is documented in
[docs/control-plane/evaluation.md](control-plane/evaluation.md). It preserves
the distinction between fixture-backed routing and live Codex evidence.

## Delivery workflow validators

The seven core delivery workflows have additional fixture-backed validators for
objective artifact invariants. Run the complete set with:

```text
python scripts/run_delivery_evaluation.py
```

These checks cover structure and safety properties such as evidence/assumption
separation, observable criteria, verification evidence, read-only review, and
pre-mutation Git inspection. Subjective quality remains manual review.

## Deterministic routing contract

The normalized routing corpus is [benchmarks/routing/cases.json](../benchmarks/routing/cases.json), governed by [benchmarks/routing/schema.json](../benchmarks/routing/schema.json). It combines the existing routing fixtures and Core behavioral cases, including explicit exclusion, ambiguity, and counterfactual boundary groups. Validate it offline with:

```text
python scripts/validate_routing_benchmark.py
```

This contract records routing evidence; it does not claim that implicit routing is measurable.

## Versioned routing baseline comparison

Create a metadata-only baseline from one or more routing result artifacts:

```text
python scripts/compare_routing_baseline.py create evals/codex/results/latest.json --output benchmarks/routing/baseline.json
```

The version-1 format is defined by [benchmarks/routing/baseline-schema.json](../benchmarks/routing/baseline-schema.json). It stores case IDs, expected/actual route labels, verdict booleans, availability, counterfactual groups, and runtime versions; it never stores prompts, transcripts, or response bodies.

Compare a candidate run with the accepted baseline; raw routing result artifacts are normalized automatically:

```text
python scripts/compare_routing_baseline.py compare benchmarks/routing/baseline.json evals/codex/results/latest.json --policy policy.json --output evals/codex/results/routing-comparison.json
```

The comparison reports per-skill accuracy deltas, new and resolved confusion edges, forbidden activation regressions, counterfactual regressions/improvements, UNKNOWN/UNAVAILABLE deltas, and overall metrics with counts. Policy checks are independent: for example, `{"zero_new_forbidden_activations": true, "protected_core_max_accuracy_regression": 0.0, "unknown_unavailable_tolerance": 0.05, "protected_core_skills": ["feature-implementation"]}`. There is no single global pass threshold. Runtime or Codex version changes are explicitly flagged as weaker causal evidence, while noisy live measurements can use a configured tolerance.

Intended workflow: change skill metadata → compile registry → run routing benchmark → create/compare against the accepted baseline → inspect semantic regressions.
