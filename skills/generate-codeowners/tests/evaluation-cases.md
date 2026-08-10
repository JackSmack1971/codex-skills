# Manual evaluation cases (not automated tests)

1. **Normal:** Given ownership history and verified GitHub owners, produce valid CODEOWNERS entries with evidence.
2. **Negative:** Given no verified owner handle, leave it unresolved rather than inventing an account.
3. **Boundary:** Given overlapping risky paths, preserve the specific rule and flag ambiguity.
