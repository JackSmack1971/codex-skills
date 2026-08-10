# Manual evaluation cases (not automated tests)

1. **Normal:** Given reviewed changes, create a concise Conventional Commit with an accurate scope.
2. **Negative:** Given unrelated or unreviewed changes, refuse to stage them implicitly.
3. **Boundary:** Given a dirty worktree with generated files, preserve them and stage explicit paths only.
