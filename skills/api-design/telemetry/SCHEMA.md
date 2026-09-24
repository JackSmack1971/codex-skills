# Telemetry schema for api-design

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `48efe9eb81bc9994b38441e09e161c07107735e55f67050f2041cd45e19b0cfa`

## Event classes

- `run.started`, `run.finished`
- `skill.invocation`
- `precondition`
- `decision`
- `operation`
- `verification`
- `failure`, `retry`
- `user.correction`, `agent.error`
- `eval.result`, `lesson.candidate`
- `hook.observation`, `usage`

## Attribution

- `semantic`: target-owned event with target fingerprint.
- `confirmed`: imported/correlated evidence known to exercise this skill.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.
