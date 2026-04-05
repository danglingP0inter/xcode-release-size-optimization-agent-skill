---
name: xcode-size-benchmark
description: Measure iOS release build artifacts and normalize size evidence for app bundles, IPA exports, frameworks, resources, and plug-ins. Use when a release-size baseline or verification re-run is needed.
---

# Xcode Size Benchmark

Use this skill to create the baseline and verification evidence in `.size-analysis/`.

## Procedure

1. Prefer a reproducible release archive path.
   - Use `python3 scripts/measure_release.py --workspace-root . --workspace ... --scheme ...`
   - Fall back to `--project` when no workspace exists.
   - Use `--app-path` and optional `--ipa-path` when artifacts already exist.
   - Use `--strip-swift-symbols` or `--no-strip-swift-symbols` to control export-time Swift symbol stripping.
   - Use `--thinning` only when you intentionally want a non-default local export variant; leave it as `none` for App Store-oriented baselines.
2. Preserve evidence.
   - Keep `baseline.json`, compatibility warnings, and Xcode logs.
   - Never overwrite prior before/after evidence without telling the user.
3. Treat missing measurements honestly.
   - If export fails or IPA creation is unavailable, leave the metric null and surface the warning.
   - If export fails because signing assets are unavailable, an unsigned packaged IPA fallback is acceptable for local size approximation as long as the report says so clearly.

## Guardrails

- Do not infer shipping size from debug builds.
- Do not mutate project settings while benchmarking.
- Keep the artifact folder stable at `.size-analysis/`.
