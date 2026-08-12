# Verification

- Offline unit tests resolve the default destination to `$HOME/.agents/skills` with an isolated HOME and verify that explicit `--dest` still receives copied skills.
- No network access or real user-home writes are required by the installer tests.
- Python AST and repository validation cover the helper scripts and canonical catalog.
