# Telemetry schema for integration-engineering

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `d11f3a430ee660bde54b037b73fb942c9ec394e575ea88f18d5a92593deee1b7`

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

## Tailored signals for this skill

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. They measure whether the
integration is actually built to survive unreliable networks, providers, and
requests — this skill's own stated purpose — not just that code was written.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`api`, `sdk`, `webhook`, `oauth`, `other`) | Which kind of provider integration was built or reviewed. | Lets an improvement agent see whether failure modes cluster on a particular integration type (e.g. webhooks systematically missing duplicate handling). |
| `decision` | `configure` | `credentials_source` | enum (`env`, `secret_manager`, `other`) | Where configuration/credentials boundaries were sourced. | Surfaces whether the skill defaults to ad hoc credential handling instead of the "existing secret mechanism" the compatibility line requires. |
| `decision` | `configure` | `fails_fast_on_missing_config` | boolean | Whether missing required configuration failed early. | Directly measures step 2's "fail early when required configuration is absent." |
| `decision` | `configure` | `sandbox_mode_used` | boolean | Whether sandbox/test mode was identified and used (step 1). | Distinguishes runs validated against a sandbox from those tested only against production semantics. |
| `decision` | `implement` | `timeout_set` / `idempotency_handled` | boolean | Whether the minimal request/event flow set timeouts and idempotency (step 3). | Directly measures step 3's core reliability requirements. |
| `decision` | `implement` | `retry_strategy` | enum (`none`, `fixed`, `exponential_backoff`, `idempotency_key`) | The retry rule chosen. | Flags integrations with `none` on operations that plausibly need retries, or retries applied without idempotency safeguards. |
| `decision` | `implement` | `webhook_signature_verified` / `duplicate_handling` | boolean or null | For webhooks, whether authenticity was verified and duplicates handled (step 4); null when not a webhook. | Directly measures step 4's webhook-specific requirements. |
| `verification` | `verify` | `scenarios_verified` | array of enum (`success`, `provider_failure`, `timeout`, `rate_limit`, `malformed_response`, `repeated_delivery`) | Which of step 6's six named verification scenarios were actually exercised. | The primary coverage signal — a chronically partial set means the skill is skipping its own required verification matrix. |
| `run.finished` | `finish` | `integration_type` / `retry_strategy` / `scenarios_verified_count` | mixed | Run summary. | Cross-run aggregation surface for the fields above. |
| `run.finished` | `finish` | `test_mode_coverage_added` / `metrics_added` / `runbook_added` | boolean | Whether step 5's test-mode coverage, metrics, and failure/recovery runbook were added. | Tracks the operational-readiness half of the skill's deliverable, not just the request/event flow. |

An improvement agent should watch the completeness of `scenarios_verified`
against the full six-item set, and cross-tabulate `retry_strategy` and
`webhook_signature_verified`/`duplicate_handling` against `task_category` to
find integration types where this skill's reliability guidance is being
under-applied.
