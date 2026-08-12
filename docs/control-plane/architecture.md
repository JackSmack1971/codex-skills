# Codex control-plane architecture

This repository separates canonical skill packages, project policy, runtime
control surfaces, correctness checks, and experiments. The initial directory
skeleton is deliberately inert: it defines ownership boundaries without
enabling rules, hooks, workers, permissions, network access, MCP servers, or
model selection.

## Responsibility map

| Surface | Responsibility |
|---|---|
| `AGENTS.md` | Normative project policy for work performed in this repository. |
| `.codex-plugin/plugin.json` | Root plugin identity and bundled-component manifest. |
| `.agents/plugins/marketplace.json` | Repo marketplace entry for distributing the root Git-backed plugin. |
| `skills/` | Canonical authoring and packaging source for all 50 skills. |
| `.agents/skills/` | Inert compatibility/discovery layer; not a canonical or generated skill tree. |
| `.codex/config.toml` | Project environment and capability defaults, if deliberately introduced in a future change. It is not created by the inert skeleton. |
| `.codex/rules/` | Command authorization. It remains empty until rules are explicitly reviewed and activated. |
| `.codex/hooks/` | Lifecycle and interception behavior. It remains empty until hooks are explicitly reviewed and activated. |
| `.codex/agents/` | Isolated worker definitions. It remains empty until custom workers are explicitly reviewed and activated. |
| `tests/` and CI | Artifact correctness and deterministic repository validation. |
| `evals/codex/` | Control-plane experimentation: authored tasks, expected invariants, graders, and generated results. |

## Skill ownership and compatibility

`skills/` remains the canonical location for all skill packages. No canonical
package is moved into or duplicated under the control plane.

`.agents/skills/` will initially be only a compatibility and discovery layer.
Its presence must not cause repository validation to count its contents as
canonical skill packages; canonical inventory and quality checks continue to
read only `skills/`.

The root plugin packages those same directories directly through
`.codex-plugin/plugin.json`; it does not copy them into `plugins/`,
`.agents/`, or `.codex/`. The repo marketplace distributes that root plugin
from GitHub. Personal standalone skill installation is a separate user-level
workflow into `$HOME/.agents/skills` and does not change this repository's
canonical source.

## Evaluation artifacts

Source tasks, graders, and expected invariants under `evals/codex/` are authored
artifacts and remain trackable. Generated or runtime output belongs under
`evals/codex/results/` and is ignored, apart from the marker that preserves the
directory itself.
