# Visual recap guidance

This reference contains the detailed review doctrine behind the thin
`SKILL.md` activation surface.

## Recap construction

Read the complete work unit and derive the recap mechanically from the actual
diff. Inventory changed routes, components, dialogs, roles, empty/error states,
and shared abstractions. Publish a substantial Agent-Native Plan: UI headline
when relevant, short outcome narrative, schema/API blocks when changed,
changed-file tree, then focused key-file diffs or annotated code.

Use wireframes for rendered UI changes, with before/after when comparison helps,
after-only for additive changes, and a sequence when the change is stateful or
responsive. Keep the visual surface realistic and grounded in changed labels,
states, components, and paths. Read `references/wireframe.md` before authoring
any wireframe and visually inspect rendered output when a browser is available.

## Structured evidence

Read the live block catalog before authoring; exact tags, required `id` fields,
props, and schemas drift. Use `data-model` for schema changes, `api-endpoint`
for contracts, `file-tree` for every changed file, split `diff` for meaningful
before/after code, and `annotated-code` for genuinely new code. Ground every
structured block in the real diff; mark inference in prose and omit facts the
diff cannot prove. Keep key changes in a horizontal tabs group with a summary
and a few high-signal annotations. Examples must be one valid JSON value.

Keep recap construction bounded: use 3–8 key-change tabs, focused excerpts
under roughly 150 lines per tab, a title of at most roughly 70 characters, and
a one-to-three-sentence brief. These limits keep a recap reviewable rather than
turning it into a raw diff dump.

The recap is lean but not skeletal: omit boilerplate and redundant prose, not
review-critical implementation evidence. Put the objective, compatibility
risk, important decisions, and review notes in outcome-first narrative blocks.

## Publication and safety

Select local-files mode whenever the user forbids hosted or database writes or
sets `AGENT_NATIVE_PLANS_MODE=local-files`. In that mode, do not call
`create-visual-recap`, `update-visual-plan`, `get-plan-feedback`, or any other
hosted Plan tool; run the local check and serve the local bridge. Otherwise
report only the absolute URL returned by the plan service; never guess an
origin. Private recaps are org/login gated. Redact API keys, tokens, signing
secrets, credential-looking literals, and private environment values from all
blocks, captions, and notes. Treat reviewer annotations as structured input;
route them back to the relevant plan or code change.

If the Plan connector or block catalog is unavailable, stop and tell the user
to run `npx -y @agent-native/core@latest reconnect https://plan.agent-native.com --client codex`,
start a new Codex session, choose Authenticate/Reconnect, and reload the
client's MCP tools. Use `--client all` to refresh every configured client.

Stop when the connector/block catalog cannot be validated, a required diff or
visual fact is unavailable, a secret cannot be safely redacted, or the recap
would require inventing a route, schema, state, or implementation detail.
