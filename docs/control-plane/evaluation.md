# Codex runtime evaluation

The repository has four distinct validation layers:

| Layer | What it proves | Command |
|---|---|---|
| Repository validation | Catalog, skill sources, docs, and control-plane layout | `python scripts/validate_repository.py` |
| Deterministic routing benchmark | Fixture-backed routing and behavioral contracts | `python scripts/run_core_benchmark.py --deterministic-only` |
| Plugin-package validation | Root manifest, marketplace, and 50 canonical entrypoints | `python scripts/validate_plugin_package.py` |
| Codex runtime evaluation | Observed Codex CLI plugin behavior, when safely available | `python scripts/run_codex_evaluation.py --live` |

Run the new offline harness with:

```text
python scripts/run_codex_evaluation.py --deterministic-only
```

Authored runtime cases live in `evals/codex/tasks/`, their objective contract
is in `evals/codex/expected_invariants/`, and generated reports are written to
the ignored `evals/codex/results/` directory.

The live command detects the installed CLI version and registers the repository
marketplace only inside a temporary `CODEX_HOME`. It does not install into the
user's configured marketplace, cache, home, or credentials. If the isolated
probe cannot run, it reports `UNAVAILABLE`. Runtime selection is `UNKNOWN`
unless JSONL or another runtime surface explicitly names a selected or loaded
skill; response wording is not evidence.
