# Manual evaluation cases (not automated tests)

1. **Normal:** Given a new required column, provide a compatible migration, backfill, verification, and rollback plan.
2. **Negative:** Given a table too large for a blocking rewrite, reject an unsafe one-step migration.
3. **Boundary:** Given mixed old/new application versions, preserve compatibility through the deployment window.
