# Manual evaluation cases (not automated tests)

1. **Normal:** Given a feature request, run a failing test, minimal implementation, and passing test in order.
2. **Negative:** Given a green test before the change or a skipped failing stage, reject the cycle as unproven.
3. **Boundary:** Given a missing local test runner, report the environment blocker instead of claiming green.
