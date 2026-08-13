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

The live command requires a dedicated persistent evaluation home. Set it once,
authenticate it, and reuse it for burn-in; do not copy `auth.json` from the
normal Codex home:

```text
CODEX_EVAL_HOME=$HOME/.codex-eval codex login
# PowerShell: $env:CODEX_EVAL_HOME="$HOME\.codex-eval"; codex login
```

Pass the same home explicitly or through the environment:

```text
python scripts/run_codex_evaluation.py --live --codex-home "$CODEX_EVAL_HOME" --case routing-grill-me-1
# equivalent: CODEX_EVAL_HOME=$HOME/.codex-eval python scripts/run_codex_evaluation.py --live
```

The runner stages the exact current checkout (including its `git_commit`) in
a temporary local marketplace, registers the marketplace root containing
`.agents/plugins/marketplace.json`, explicitly installs `codex-skills`, and
verifies that the installed plugin is exposed before `codex exec`. It does not
use `--ignore-user-config`, because the dedicated home’s config is part of the
isolated evaluation. Setup failures report one of `authentication`,
`marketplace_registration`, `plugin_installation`, or `plugin_exposure` and
retain the CLI diagnostic. Missing runtime or selection telemetry is
`RUNTIME_FAILURE`, `PLUGIN_UNAVAILABLE`, or `INSTRUMENTATION_UNAVAILABLE`, never
a routing pass. Before implicit cases, calibration explicitly invokes
`$testing-qa` and requires its injected marker. Only a successful calibration
enables routing measurement. The stage-only marker is a deterministic,
nonce-bound read-only command injected into each staged SKILL.md body; parsing
accepts it only from structured `item.*` command-execution events. Native
`skill_selected`/`skill_loaded` events remain supported if they appear, but are
not required. Every artifact and baseline records
`measurement_method: "injected-skill-marker-v1"`; baselines with another
method are incompatible.

## Burn-in workflow

Run a small trial set into unique artifacts, then build one metadata-only baseline:

```text
python scripts/run_codex_evaluation.py --live --group front-door --limit 5 --output evals/codex/results/burn-in-01.json
python scripts/run_codex_evaluation.py --live --group front-door --limit 5 --output evals/codex/results/burn-in-02.json
python scripts/compare_routing_baseline.py create evals/codex/results/burn-in-01.json evals/codex/results/burn-in-02.json --output evals/codex/results/burn-in-baseline.json
```

Each case retains every trial and reports counts/rates. Trial metadata includes the run ID, timestamp, commit, runtime version, and Codex version; prompts, response bodies, transcripts, reasoning, secrets, and private runtime data remain excluded. Use `--case` for one case; omitting `--output` keeps the default `evals/codex/results/latest.json` behavior.
