---
name: tailwind-design-system
description: "Build production-ready Tailwind design systems with tokens, variants, responsive patterns, and accessibility."

---

# Tailwind Design System

## Version gate

Before giving version-sensitive setup or configuration guidance, establish the
project's Tailwind major version from repository evidence. Check, in order:

1. `package.json` dependencies/devDependencies and the resolved package in the
   lockfile or installed package metadata.
2. The package manager's dependency tree when repository files are insufficient.
3. Existing CSS/configuration only as corroborating evidence, not as a version
   substitute.

If evidence is missing or conflicting, say that the version is unknown and stop
before recommending version-sensitive setup. Do not silently choose v3 or v4.

Use the matching playbook section:

- **Tailwind v4:** CSS-first configuration with `@import "tailwindcss"`,
  `@theme`, and automatic source detection where applicable.
- **Tailwind v3:** JavaScript/TypeScript configuration with `content` paths and
  `@tailwind base;`, `@tailwind components;`, and `@tailwind utilities;`.

Keep the design-token, component-variant, responsive, dark-mode, and
accessibility guidance below version-neutral unless a section is explicitly
marked v3 or v4. Never mix the two setup patterns without explaining the
compatibility reason and confirming the project's version.

Build production-ready design systems with Tailwind CSS, including design tokens, component variants, responsive patterns, and accessibility.

## Use this skill when

- Creating a component library with Tailwind
- Implementing design tokens and theming
- Building responsive and accessible components
- Standardizing UI patterns across a codebase
- Migrating to or extending Tailwind CSS
- Setting up dark mode and color schemes

## Do not use this skill when

- The task is unrelated to tailwind design system
- You need a different domain or tool outside this scope

## Instructions

- Clarify goals, constraints, and required inputs.
- Apply relevant best practices and validate outcomes.
- Provide actionable steps and verification.
- If detailed examples are required, open `resources/implementation-playbook.md`
  after the version gate succeeds.

## Resources

- `resources/implementation-playbook.md` for detailed patterns and examples.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before the version gate, start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<component_library|design_tokens|responsive_accessible|pattern_standardization|migration|dark_mode_setup>" --invocation explicit)
   ```
   If `python3` is unavailable, use `python`.
2. After the version gate resolves (or fails to), record the version
   decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase version_gate --outcome <success|failure> \
     --evidence-json '{"tailwind_version":"<v3|v4|unknown>","evidence_source":"<package_json|lockfile|dependency_tree|css_config|insufficient>","stopped_due_to_unknown":<true|false>}'
   ```
3. After selecting and applying the matching v3/v4 playbook section
   (Instructions: "apply relevant best practices and validate outcomes"),
   record what was applied:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event operation --phase apply_playbook \
     --evidence-json '{"playbook_loaded":<true|false>,"version_neutral_sections_used":["<subset of design_tokens,component_variants,responsive,dark_mode,accessibility>"],"mixed_setup_flagged":<true|false>}'
   ```
4. Before returning output, close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"tailwind_version":"<v3|v4|unknown>","task_category":"<component_library|design_tokens|responsive_accessible|pattern_standardization|migration|dark_mode_setup>","playbook_loaded":<true|false>}'
   ```
   Use `--outcome failure` with a `--failure-class` (`version_unknown`) when
   the version gate could not establish a version and guidance stopped
   before any version-sensitive setup, per the Version gate section.

If a maintainer later reports the detected Tailwind version was wrong,
record it as its own event so drift in the version gate's accuracy is
visible without re-running the guidance:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"original_tailwind_version":"<v3|v4|unknown>","correction":"version_misdetected","corrected_version":"<v3|v4>"}'
```


