---
name: xcode-size-orchestrator
description: Coordinate iOS release build size analysis, generate a shareable optimization plan, and drive approval-gated fixes. Use when asked to reduce app size, optimize IPA size, investigate archive bloat, or prepare an app for App Store submission size review.
---

# Xcode Size Orchestrator

Use this skill as the entry point for release-size work. It coordinates measurement, specialist analysis, reporting, and approved remediation.

## Workflow

1. Establish the support level.
   - Check the workspace for Xcode-native project files, SwiftPM resolution, CocoaPods, Carthage, and unusual packaging signals.
   - Read [compatibility](../../references/compatibility.md) if support boundaries may affect confidence.
2. Produce a baseline.
   - Run `python3 scripts/measure_release.py ...` to create `.size-analysis/baseline.json` and compatibility notes.
   - Run `python3 scripts/analyze_macho.py <app-path> --output .size-analysis/top_binaries.json`.
   - Run `python3 scripts/analyze_resources.py <app-path> --output .size-analysis/top_resources.json`.
   - Run `python3 scripts/analyze_swiftpm.py <workspace-root> --output .size-analysis/swiftpm-summary.json`.
3. Synthesize findings.
   - Map findings to [size checks](../../references/size-checks.md).
   - Keep recommendations evidence-based, ranked, and risk-labeled.
4. Render the plan.
   - Run `python3 scripts/render_report.py`.
   - The report path must be `.size-analysis/size-optimization-plan.md`.
5. Stop before mutation.
   - Do not change project files during analysis.
   - Ask for explicit approval before invoking the fixer.

## Output contract

- Primary artifact: `.size-analysis/size-optimization-plan.md`
- Supporting artifacts: `.size-analysis/*.json`, build logs, and any before/after comparison files

## When to load references

- Read [measurement contract](../../references/measurement-contract.md) when deciding what must be captured.
- Read [report format](../../references/report-format.md) when composing or validating the markdown plan.
- Read [fixer scope](../../references/fixer-scope.md) before implementing approved changes.
