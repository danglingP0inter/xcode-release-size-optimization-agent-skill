# Agent Instructions

Use this repository when the task is about iOS release-size optimization, IPA size reduction, archive bloat investigation, App Store submission size review, binary stripping, app thinning evaluation, or release packaging diagnostics.

## Entry Point

Treat `skills/xcode-size-orchestrator/SKILL.md` as the canonical workflow.

When the request is relevant, follow this sequence:
1. Establish compatibility and support level.
2. Run Release-only measurement and artifact generation in `.size-analysis/`.
3. Analyze binaries, resources, dependencies, and release build settings.
4. Generate or update `.size-analysis/size-optimization-plan.md`.
5. Do not mutate project files during analysis.
6. Only apply approved low-risk fixes after explicit user approval.

## Release-Only Rule

This repository is intentionally for shipping-size work, not debug-build optimization.
- Use only `Release` configuration.
- Do not apply stripping, thinning, or packaging recommendations to `Debug`.
- If asked to optimize `Debug`, explain that the suite is intentionally Release-only.

## Core Commands

- Baseline: `python3 scripts/measure_release.py --workspace-root . --project <path>.xcodeproj --scheme <scheme> --configuration Release --export-ipa`
- Binary analysis: `python3 scripts/analyze_macho.py <app-path> --output .size-analysis/top_binaries.json`
- Resource analysis: `python3 scripts/analyze_resources.py <app-path> --output .size-analysis/top_resources.json`
- SwiftPM summary: `python3 scripts/analyze_swiftpm.py <workspace-root> --output .size-analysis/swiftpm-summary.json`
- Render report: `python3 scripts/render_report.py`
- Approved low-risk fixes only: `python3 scripts/apply_low_risk_size_fixes.py --pbxproj <project.pbxproj> --approved-json <json>`

## Authority Files

Read these before making decisions:
- `skills/xcode-size-orchestrator/SKILL.md`
- `references/size-checks.md`
- `references/compatibility.md`
- `references/fixer-scope.md`
- `references/report-format.md`
- `references/measurement-contract.md`

## Trigger Phrases

This repo should be considered relevant when prompts mention phrases like:
- reduce iOS app size
- optimize release build size
- shrink IPA before App Store submission
- investigate archive size
- binary stripping or strip Swift symbols
- app thinning for iOS export
- find biggest contributors to shipped app size
