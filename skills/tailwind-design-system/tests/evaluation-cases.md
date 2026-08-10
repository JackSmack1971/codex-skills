# Tailwind Design System evaluation cases (not automated tests)

These cases are deterministic review fixtures: inspect the named evidence and
compare the response with the required and forbidden behaviors.

1. **Normal:** A repository's `package.json` and lockfile resolve
   `tailwindcss@4.x`. The response must identify v4 before setup guidance and
   use `@import "tailwindcss"` plus `@theme`; it must not default to a
   `content` array or the three v3 `@tailwind` directives. Version-neutral
   token, variant, responsive, dark-mode, and accessibility guidance remains.
2. **Negative:** A repository's dependency evidence resolves `tailwindcss@3.x`.
   The response must identify v3 and may use `tailwind.config.ts`, `content`,
   and the three v3 `@tailwind` directives. It must not present v4 CSS-first
   setup as the project's default.
3. **Boundary:** A repository has no Tailwind dependency evidence, or package
   metadata conflicts with its config files. The response must report that the
   major version is unknown/conflicting, request or gather evidence, and stop
   version-sensitive setup guidance. It must not silently assume v3 or v4.
4. **Preservation:** Across all three cases, verify that token hierarchy,
   component variants, responsive patterns, dark mode, focus states, ARIA
   guidance, and the detailed implementation playbook remain available.
