# Measurement Contract

The suite writes all evidence to `.size-analysis/` and treats those files as the source of truth for follow-up analysis and verification.

## Required artifacts

- `baseline.json`: normalized metadata for the most recent baseline run
- `comparison.json`: before/after deltas when a verification pass exists
- `size-optimization-plan.md`: primary human-readable report
- `top_resources.json`: ranked resource entries by size
- `top_binaries.json`: ranked executable and framework entries by size
- `swiftpm-summary.json`: package-resolution and package-footprint summary when SwiftPM is present
- `compatibility.json`: support-matrix findings and degraded-mode warnings

## Baseline contents

Each baseline should capture:

- project context and invocation arguments
- archive, app bundle, and IPA paths when present
- app bundle size
- executable size
- embedded framework totals
- plug-in totals
- resource totals grouped by category
- architecture slices for major binaries when detectable
- dSYM or debug symbol presence when detectable
- release build settings relevant to stripping and dead-code elimination when project inputs are available
- export options relevant to stripping and thinning
- top offenders by bytes and percentage

## Normalization rules

- Always report bytes as raw integers and human-readable strings.
- Prefer paths relative to the workspace root when possible.
- Preserve unknown fields instead of silently dropping them.
- If a measurement cannot be produced reliably, include `null` and add a warning rather than inventing a value.
