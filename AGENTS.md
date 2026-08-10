# Project policy

The packages under `skills/` are the repository's canonical skill sources. Do
not move or duplicate them into project control-plane directories.

The control-plane skeleton is intentionally inert. Do not add command-blocking
rules, lifecycle hooks, model or network settings, permission settings, MCP
servers, or custom agent definitions unless a later change explicitly reviews
and activates that behavior.

`.agents/skills/` is reserved as a compatibility and procedural-discovery
layer. Content there does not replace or redefine packages under `skills/`.
