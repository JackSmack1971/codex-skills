# Manual evaluation cases (not automated tests)

1. Run `scripts/list-skills.py --format json`; assert valid JSON and an explicit installed annotation for local matches.
2. Run `scripts/install-skill-from-github.py --help`; assert the source, destination, ref, and download/git method options are exposed.
3. **Normal:** With an isolated `HOME`, confirm the default destination is `$HOME/.agents/skills` and that `--dest` overrides it without network access.
4. **Boundary:** Confirm installation is not run without a user-selected source because it writes to the user-level skill directory.
