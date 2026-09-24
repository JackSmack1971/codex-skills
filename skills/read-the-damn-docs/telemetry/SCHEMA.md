# Telemetry schema for read-the-damn-docs

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `f7c30ede4680458349f3415097ca4b8d8926fe5f9022331970a850f3aa1b3cd8`

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
- `correlated`: hook-observed execution evidence (tool calls, commands, exit codes) automatically attached to the semantic run that was open in the same session when it fired; included in analysis by default, but is a best-effort session-scoped join, not proof the tool call belongs to this skill's own logic.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence outside any open run; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether this skill
actually grounds its answer in authoritative docs rather than model memory.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`package_add_or_upgrade`, `provider_api_or_auth`, `error_or_deprecation`, `local_repo_contract`, `irreversible_choice`, `explicit_request`) | Which Docs-First Trigger category fired. | Lets an improvement agent see whether a particular trigger category (e.g. `error_or_deprecation`) correlates with weaker docs grounding downstream. |
| `verification` | `search` | `docs_already_local` | boolean | Whether the docs were already in the repo/supplied, skipping a web search. | Distinguishes legitimate local-first shortcuts from missed web searches. |
| `verification` | `search` | `web_search_performed` | boolean | Whether a web search for official docs was actually run. | Directly measures the Required Workflow's core requirement; a false rate on a non-local task is a compliance failure. |
| `verification` | `search` | `source_domain` | enum (`official_product_docs`, `package_registry`, `local_repo`, `source_code_types`, `other`) | Which "What Counts As Docs" category the evidence came from. | Flags drift toward `other` (Stack Overflow, blogs, memory) instead of authoritative sources. |
| `decision` | `extract` | `facts_extracted_count` | integer | Number of concrete facts pulled from the docs in step 4. | A near-zero count after a successful search suggests the search happened but wasn't actually used. |
| `decision` | `extract` | `breaking_changes_found` | boolean | Whether a breaking change was surfaced. | Confirms the extraction step actually checks for version-sensitive breaking changes, not just happy-path syntax. |
| `decision` | `extract` | `version_verified` | boolean | Whether the current/target package version was verified before writing imports or config. | Directly measures the "verify the latest version before writing imports" rule for new packages. |
| `verification` | `verify_check` | `check_type` | enum (`typecheck`, `tests`, `build`, `cli_dry_run`, `api_schema_validation`, `local_reproduction`, `none`) | Which step-6 verification method was used. | A persistently `none` value on implementation tasks flags that the required smallest-useful-check step is being skipped. |
| `verification` | `verify_check` | `check_passed` | boolean | Whether the chosen check passed. | Separates "docs were followed but the check still failed" from clean runs. |
| `run.finished` | `finish` | `docs_named_in_answer` | boolean | Whether the docs or local files consulted were named in the final answer. | Directly measures compliance with step 7's citation requirement. |
| `run.finished` | `finish` | `docs_unavailable_disclosed` | boolean | Whether unavailability of docs was disclosed plainly instead of silently falling back to memory. | Directly measures the "If Docs Are Unavailable" section's disclosure requirement. |

An improvement agent should watch the rate of `web_search_performed == false`
on non-local tasks, the distribution of `source_domain` (watching for
`other` creeping up), and whether `docs_named_in_answer` stays high across
`task_category` values, to decide whether the Required Workflow section of
`SKILL.md` needs revision.
