# Manual evaluation cases (not automated tests)

1. **Normal:** Given parallel branch work, create and verify an isolated worktree with the expected branch and path.
2. **Negative:** Given an existing dirty target path, stop instead of overwriting it.
3. **Boundary:** Given a cleanup request, verify the exact worktree and branch state before removal.
