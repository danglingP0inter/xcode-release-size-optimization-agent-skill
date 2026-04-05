---
name: xcode-size-fixer
description: Apply approved low-risk release-size optimizations for iOS projects, then re-measure and verify the impact. Use only after the optimization plan exists and the user has clearly approved specific items.
---

# Xcode Size Fixer

Use this skill only after `.size-analysis/size-optimization-plan.md` exists and the user has approved specific items.

## Procedure

1. Read `.size-analysis/size-optimization-plan.md`.
2. Load [fixer scope](../../references/fixer-scope.md).
3. Implement only explicitly approved low-risk items.
   - For approved build-setting toggles, prefer `python3 scripts/apply_low_risk_size_fixes.py --pbxproj <project.pbxproj> --approved-json <json>`.
4. Re-run measurement and comparison:
   - `python3 scripts/measure_release.py ... --run-label after`
   - `python3 scripts/compare_runs.py <before> <after> --output .size-analysis/comparison.json`
   - `python3 scripts/render_report.py`
5. Summarize what changed and what the new evidence shows.

## Hard rules

- Do not apply unapproved medium-risk or advisory-only items.
- Stop if the project fails to build or archive after changes.
- Keep verification evidence in `.size-analysis/`.
