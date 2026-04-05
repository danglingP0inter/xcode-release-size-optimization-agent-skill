---
name: xcode-release-size-optimization
description: Use this skill when asked to reduce iOS app size, optimize IPA or archive size, investigate release build bloat, evaluate stripping or thinning, or prepare an app for App Store submission size review.
---

# Xcode Release Size Optimization

This is the external-agent entry skill for this repository.

## When to use it

Use this skill when the user wants to:
- reduce iOS app size
- optimize Release build size
- shrink an IPA before App Store submission
- investigate why an archive is too large
- review binary stripping or app thinning behavior

## Workflow

1. Read `skills/xcode-size-orchestrator/SKILL.md` and follow it as the canonical workflow.
2. Keep analysis read-only and evidence-first.
3. Generate artifacts in `.size-analysis/`.
4. Use only `Release` configuration.
5. Generate `size-optimization-plan.md` before proposing project mutations.
6. Apply only approved low-risk fixes.

## Key commands

- `python3 scripts/measure_release.py --workspace-root . --project <path>.xcodeproj --scheme <scheme> --configuration Release --export-ipa`
- `python3 scripts/analyze_macho.py <app-path> --output .size-analysis/top_binaries.json`
- `python3 scripts/analyze_resources.py <app-path> --output .size-analysis/top_resources.json`
- `python3 scripts/analyze_swiftpm.py <workspace-root> --output .size-analysis/swiftpm-summary.json`
- `python3 scripts/render_report.py`

## Guardrails

- This workflow is Release-only.
- Do not optimize `Debug` builds.
- Do not apply fixes without explicit approval.
- Treat stripping and debug-info changes as medium risk unless clearly safe.
- Treat thinning as optional and contextual, especially for `app-store` exports.
