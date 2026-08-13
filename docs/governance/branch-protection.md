# Default branch protection

The `main` branch is protected through GitHub repository settings. Changes
must arrive through pull requests and pass the repository validation workflow.
Direct pushes and force-pushes are disabled; administrators should bypass the
rule only for an emergency recovery that is documented in the issue tracker.

The required validation status is the workflow check produced by
`.github/workflows/validate-skills.yml`. Keep required checks limited to jobs
that run for every eligible pull request so the rule does not deadlock routine
maintenance.

The scheduled/manual `Experimental routing evaluation` workflow is not a
required check. It measures runtime selection separately from deterministic
validation and must not replace or weaken the required checks above.
