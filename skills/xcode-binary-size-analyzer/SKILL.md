---
name: xcode-binary-size-analyzer
description: Analyze iOS app executables, embedded frameworks, linker-related contributors, and architecture slices for release-size optimization. Use when binary or framework size appears to dominate the shipped app.
---

# Xcode Binary Size Analyzer

Use this skill after a baseline exists and the app bundle path is known.

## Procedure

1. Run `python3 scripts/analyze_macho.py <app-path> --output .size-analysis/top_binaries.json`.
2. When project inputs are available, run `python3 scripts/analyze_build_settings.py --workspace-root . --project ... --scheme ... --output .size-analysis/build-settings.json`.
3. Review the main executable, embedded frameworks, architecture slices, and release stripping settings.
4. Map concrete findings to binary checks in [size checks](../../references/size-checks.md).
5. Keep recommendations specific:
   - oversized frameworks
   - release optimization setting issues
   - symbol stripping or debug payload concerns
   - unexpected architecture slices

## Guardrails

- Prefer advisory recommendations for framework replacement or linkage strategy changes.
- Mark anything that could affect symbolication or debugging as medium risk or higher.
