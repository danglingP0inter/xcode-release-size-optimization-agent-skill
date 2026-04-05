---
name: xcode-dependency-size-analyzer
description: Analyze Swift Package Manager dependencies and packaged third-party frameworks for release-size impact, while detecting unsupported dependency managers. Use when dependency choices may be bloating the app.
---

# Xcode Dependency Size Analyzer

Use this skill to explain dependency-related shipping cost.

## Procedure

1. Run `python3 scripts/analyze_swiftpm.py <workspace-root> --output .size-analysis/swiftpm-summary.json`.
2. Combine package metadata with `.size-analysis/top_binaries.json` and `.size-analysis/top_resources.json`.
3. Surface limited-support signals early if CocoaPods, Carthage, or custom packaging is present.
4. Prefer evidence-backed dependency guidance over abstract package criticism.

## Typical findings

- large SwiftPM packages visible in bundled frameworks
- transitive package bloat worth manual review
- vendored frameworks with heavy shipping cost
- debug or demo resources leaking into release packaging

## Guardrails

- Do not invent per-package byte attribution when the bundle evidence is ambiguous.
- Treat package replacement or package graph restructuring as advisory work.
