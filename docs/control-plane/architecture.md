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
| `.agents/skills/` | Project-local procedural discovery. |
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

## Evaluation artifacts

Source tasks, graders, and expected invariants under `evals/codex/` are authored
artifacts and remain trackable. Generated or runtime output belongs under
`evals/codex/results/` and is ignored, apart from the marker that preserves the
directory itself.
