# Manual evaluation cases (not automated tests)

1. **Normal:** Given a PR diff with a defect, produce a severity-ranked finding citing file, lines, impact, and fix direction.
2. **Negative:** Given only a title and no repository or diff evidence, refuse to claim review completion.
3. **Boundary:** Given a clean diff and requested GitHub review, stay read-only unless posting is explicitly authorized.
