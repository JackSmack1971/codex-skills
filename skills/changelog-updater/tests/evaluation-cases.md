# Manual evaluation cases (not automated tests)

1. **Normal:** Given a tagged Git range, classify user-facing changes and update the correct changelog section.
2. **Negative:** Given ambiguous commits with no diff evidence, preserve uncertainty rather than inventing release notes.
3. **Boundary:** Given security or breaking changes, retain the required disclosure and verify the rendered result.
