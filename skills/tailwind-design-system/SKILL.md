---
name: tailwind-design-system
description: "Build production-ready design systems with Tailwind CSS, including design tokens, component variants, responsive patterns, and accessibility."
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


