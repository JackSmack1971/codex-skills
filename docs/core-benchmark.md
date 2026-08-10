# Core skill benchmark

The benchmark manifest is [`benchmarks/core/manifest.json`](../benchmarks/core/manifest.json). It contains one representative task and positive, negative, and ambiguous trigger cases for each of the 23 Core skills.

Run the baseline (deterministic checks plus one explicit model-backed sample when `codex` is installed):

```text
python scripts/run_core_benchmark.py --output benchmarks/core/baseline.json
```

Use `--deterministic-only` for an offline run, or `--runs 3` to repeat the model-backed sample. The report records the manifest, UTC timestamp, task identity, run count, exit code, response digest/size, pass criteria, and uncertainty. It deliberately omits response bodies, transcripts, and secrets.

Measurement modes are separate. Explicit cases name `$skill` in the prompt. Implicit selection is currently **unavailable and unreported** because the local Codex CLI does not expose selected-skill telemetry; explicit results must not be read as implicit trigger accuracy. Model responses are human-review material, not fake objective scores.
