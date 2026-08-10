# Core skill benchmark

The benchmark manifest is [`benchmarks/core/manifest.json`](../benchmarks/core/manifest.json). It contains one representative task and positive, negative, and ambiguous trigger cases for each of the 23 Core skills.

Run the baseline (deterministic checks plus one explicit model-backed sample when `codex` is installed):

```text
python scripts/run_core_benchmark.py --output benchmarks/core/baseline.json
```

Use `--deterministic-only` for an offline run, or `--runs 3` to repeat the model-backed sample. The report records the manifest, UTC timestamp, task identity, run count, exit code, response digest/size, pass criteria, and uncertainty. It deliberately omits response bodies, transcripts, and secrets.

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

## Delivery workflow validators

The seven core delivery workflows have additional fixture-backed validators for
objective artifact invariants. Run the complete set with:

```text
python scripts/run_delivery_evaluation.py
```

These checks cover structure and safety properties such as evidence/assumption
separation, observable criteria, verification evidence, read-only review, and
pre-mutation Git inspection. Subjective quality remains manual review.
