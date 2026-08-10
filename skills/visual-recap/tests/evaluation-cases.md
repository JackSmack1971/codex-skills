# Manual evaluation cases (not automated tests)

1. **Normal:** Given a diff with interacting files, produce a recap matching actual files and validation.
2. **Negative:** Given no diff or commit evidence, report the missing target instead of inventing a recap.
3. **Boundary:** Given docs-only changes, avoid implying runtime behavior the diff cannot prove.
