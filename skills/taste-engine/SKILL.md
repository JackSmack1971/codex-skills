---
name: taste-engine
description: "Apply an explicitly enabled user-maintained design preference profile to UI/UX briefs."
compatibility: Requires a user-provided profile path and explicit opt-in; no profile or persistence location is assumed.
---

# Taste Engine

This is an opt-in design aid, not an always-on worker. Use it only when the user explicitly enables it and provides a JSON profile. Read the profile, select the strongest signals for fonts, colors, layout density, and aesthetic direction, and add them as suggestions to the current design brief.

Never invent a profile, infer preferences from hidden session history, write to a legacy runtime config file, or mutate a file without an explicit path and user approval. Current-turn instructions always win. Preserve the supplied JSON schema when the user explicitly requests an approved/rejected update; otherwise return a proposed JSON patch or design-token block rather than writing state.

Codex does not provide the source runtime's command registry. Treat synchronization and token application as conversational operations and keep the profile path, opt-in flag, and output artifact visible in the response.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before reading the profile, start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<advisory_suggestion|state_update>" --invocation explicit)
   ```
2. After validating the opt-in and profile (never invent a profile, never
   write to a legacy runtime config file), record the check:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase validate --outcome <success|failure> \
     --evidence-json '{"opt_in_confirmed":<true|false>,"profile_provided":<true|false>,"legacy_config_avoided":<true|false>}'
   ```
3. After selecting the strongest signals for fonts, colors, layout density,
   and aesthetic direction, record the decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase select \
     --evidence-json '{"signal_categories":["<subset of fonts,colors,layout_density,aesthetic_direction>"],"signals_selected_count":<N>}'
   ```
4. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"output_mode":"<advisory_patch|design_token_block|state_update>","signal_categories":["<subset of fonts,colors,layout_density,aesthetic_direction>"],"state_mutated":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` when the workflow stopped
   under the "never invent a profile" / no-explicit-opt-in boundary instead
   of producing output.

If the user later rejects or changes the suggested signals (e.g. dismisses a
proposed token, disputes a profile-derived preference), record it so
suggestion quality is visible without re-running the skill:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"original_output_mode":"<advisory_patch|design_token_block|state_update>","correction":"<signals_rejected|signals_modified|profile_disputed>"}'
```
