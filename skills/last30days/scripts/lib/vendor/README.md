# Vendored dependencies

The `bird-search/` directory is intentionally versioned. The `/last30days`
runtime invokes `bird-search.mjs` as a local subprocess, so the wrapper and its
small runtime dependency set are part of the skill's supported offline source
tree rather than generated output.

Keep the files synchronized with the upstream package metadata in
`bird-search/package.json`. Preserve the included `LICENSE` and review its
terms before redistribution. This documentation records the intentional vendor
boundary; it does not suppress generated-artifact findings from the repository
verifier.
