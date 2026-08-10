# Manual evaluation cases (not automated tests)

1. **Normal:** In a Git repository with a supplied diff, invoke the skill and assert findings are ordered by severity and cite changed files.
2. **Negative:** In a workspace without Git, assert the skill reports the target as unavailable rather than inventing a diff.
3. **Boundary:** Confirm the skill does not edit files, create commits, push branches, or post review comments.
