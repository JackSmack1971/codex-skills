# Contributing

## Where changes belong

Packages under `skills/` are the canonical skill sources. Keep `.agents/skills/`
as a compatibility and procedural-discovery layer; do not duplicate packages
there. Keep the inert `.codex/` skeleton unchanged unless a change explicitly
activates control-plane behavior.

## Workflow

1. Open or claim an issue and describe the files and verification you plan to
   touch.
2. Create a focused branch and keep one issue's behavior in one pull request.
3. Add or update the smallest relevant test or validator coverage.
4. Run the repository checks before requesting review:

   ```text
   python scripts/validate_repository.py
   python -m unittest discover -s tests -v
   python scripts/run_core_benchmark.py --deterministic-only
   python scripts/validate_skill_inventory.py
   git diff --check
   ```

5. Link the issue in the pull request and summarize behavior, risk, and
   verification. Do not weaken validation or security guarantees to make a
   check pass.

## Documentation and licensing

Keep inventory and documentation claims grounded in repository evidence. New
third-party material must retain its license and attribution, and new
dependencies need a clear reason and documented validation.
