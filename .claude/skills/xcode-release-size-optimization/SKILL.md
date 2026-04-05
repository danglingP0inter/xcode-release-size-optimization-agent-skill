---
name: xcode-release-size-optimization
description: Use this skill when asked to reduce iOS app size, optimize IPA or archive size, investigate release build bloat, evaluate stripping or thinning, or prepare an app for App Store submission size review.
---

# Xcode Release Size Optimization

Use this skill as the external-agent entry point for release-size work in this repository.

## Workflow

1. Start with `skills/xcode-size-orchestrator/SKILL.md`.
2. Use only `Release` configuration.
3. Keep analysis read-only and evidence-first.
4. Write artifacts to `.size-analysis/`.
5. Generate `size-optimization-plan.md` before changing project files.
6. Apply only explicitly approved low-risk fixes.

## Key commands

- `python3 scripts/measure_release.py --workspace-root . --project <path>.xcodeproj --scheme <scheme> --configuration Release --export-ipa`
- `python3 scripts/analyze_macho.py <app-path> --output .size-analysis/top_binaries.json`
- `python3 scripts/analyze_resources.py <app-path> --output .size-analysis/top_resources.json`
- `python3 scripts/analyze_swiftpm.py <workspace-root> --output .size-analysis/swiftpm-summary.json`
- `python3 scripts/render_report.py`

## Guardrails

- Release-only.
- No `Debug` size optimization.
- No unapproved fixes.
- Stripping/debug-info changes require caution.
- Thinning should be used intentionally, not implicitly.
