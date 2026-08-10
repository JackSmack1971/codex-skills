# Manual evaluation cases (not automated tests)

1. **Normal:** Given a requested branch operation, inspect status and refs before making the reversible change.
2. **Negative:** Given an unresolved merge or rebase, stop and report it rather than issuing another mutation.
3. **Boundary:** Given a destructive cleanup request, verify exact targets and require explicit approval.
