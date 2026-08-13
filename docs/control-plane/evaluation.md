# Codex runtime evaluation

The repository has four distinct validation layers:

| Layer | What it proves | Command |
|---|---|---|
| Repository validation | Catalog, skill sources, docs, and control-plane layout | `python scripts/validate_repository.py` |
| Deterministic routing benchmark | Fixture-backed routing and behavioral contracts | `python scripts/run_core_benchmark.py --deterministic-only` |
| Plugin-package validation | Root manifest, marketplace, and 50 canonical entrypoints | `python scripts/validate_plugin_package.py` |
| Codex runtime evaluation | Observed Codex CLI plugin behavior, when safely available | `python scripts/run_codex_evaluation.py --live` |

The required push/PR workflow is deterministic. It proves repository and
control-plane consistency, fixture-backed Core behavior, routing corpus/schema
validity, and grader/report behavior. It does not prove that a live Codex
runtime will select a skill.

The separate `Experimental routing evaluation` workflow runs manually or
weekly. It records runtime and Codex versions, analyzes live results, and
uploads metadata-only artifacts. Missing runtime or selection telemetry is
`UNAVAILABLE`, never a routing pass. A committed
`benchmarks/routing/baseline.json` is compared when present; this workflow is
not part of branch protection.

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

## Burn-in workflow

Run a small trial set into unique artifacts, then build one metadata-only baseline:

```text
python scripts/run_codex_evaluation.py --live --group front-door --limit 5 --output evals/codex/results/burn-in-01.json
python scripts/run_codex_evaluation.py --live --group front-door --limit 5 --output evals/codex/results/burn-in-02.json
python scripts/compare_routing_baseline.py create evals/codex/results/burn-in-01.json evals/codex/results/burn-in-02.json --output evals/codex/results/burn-in-baseline.json
```

Each case retains every trial and reports counts/rates. Trial metadata includes the run ID, timestamp, commit, runtime version, and Codex version; prompts, response bodies, transcripts, reasoning, secrets, and private runtime data remain excluded. Use `--case` for one case; omitting `--output` keeps the default `evals/codex/results/latest.json` behavior.
