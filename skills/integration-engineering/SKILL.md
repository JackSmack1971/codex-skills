---
name: integration-engineering
description: "Safely implement or review integrations with external APIs, SDKs, webhooks, OAuth, and service providers."
compatibility: Requires access to authoritative provider documentation and the repository's supported runtime/tooling; credentials must be supplied through the existing secret mechanism.
---

# Integration Engineering

Build the smallest provider integration that remains correct when networks,
providers, and requests are unreliable.

## Workflow

1. Read current authoritative provider documentation and identify supported
   API/SDK versions, sandbox mode, limits, and lifecycle requirements.
2. Define credentials/configuration boundaries and fail early when required
   configuration is absent; never print secrets.
3. Implement the minimal request or event flow with timeouts, safe error
   mapping, retry rules, and idempotency appropriate to the operation.
4. For webhooks, verify authenticity, handle duplicates, acknowledge quickly,
   and process safely.
5. Add test-mode coverage, redacted structured logs, useful metrics, and a
   failure/recovery runbook.
6. Verify success, provider failure, timeout, rate limit, malformed response,
   and repeated-delivery behavior.

## Boundary

Do not guess undocumented provider behavior or retry non-idempotent operations
blindly. Stop when credentials, provider policy, or authoritative version
information is missing.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before Workflow step 1, start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<api|sdk|webhook|oauth|other>" --invocation "<explicit|implicit|unknown>")
   ```
2. After step 2 (define credentials/configuration boundaries), record the
   configuration decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase configure \
     --evidence-json '{"credentials_source":"<env|secret_manager|other>","fails_fast_on_missing_config":<true|false>,"sandbox_mode_used":<true|false>}'
   ```
3. After steps 3-4 (implement the minimal request/event flow and, for
   webhooks, verify authenticity and handle duplicates), record the
   implementation decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase implement \
     --evidence-json '{"timeout_set":<true|false>,"retry_strategy":"<none|fixed|exponential_backoff|idempotency_key>","idempotency_handled":<true|false>,"webhook_signature_verified":<true|false|null>,"duplicate_handling":<true|false|null>}'
   ```
4. After step 6 (verify success, provider failure, timeout, rate limit,
   malformed response, and repeated-delivery behavior), record the
   verification:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase verify --outcome <success|failure> \
     --evidence-json '{"scenarios_verified":["<subset of success,provider_failure,timeout,rate_limit,malformed_response,repeated_delivery>"]}'
   ```
5. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"integration_type":"<api|sdk|webhook|oauth|other>","retry_strategy":"<none|fixed|exponential_backoff|idempotency_key>","scenarios_verified_count":<N>,"test_mode_coverage_added":<true|false>,"metrics_added":<true|false>,"runbook_added":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` when the workflow
   stopped under Boundary instead of producing a working integration.
