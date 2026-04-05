---
name: xcode-resource-size-analyzer
description: Analyze packaged iOS app resources such as asset catalogs, images, localization payloads, fonts, bundled data, and duplicate files. Use when resources may be inflating the release artifact.
---

# Xcode Resource Size Analyzer

Use this skill to explain where non-code bytes are going inside the shipping app bundle.

## Procedure

1. Run `python3 scripts/analyze_resources.py <app-path> --output .size-analysis/top_resources.json`.
2. Inspect category totals, top individual resources, and duplicate-content warnings.
3. Map findings to resource checks in [size checks](../../references/size-checks.md).
4. Recommend only evidence-backed follow-ups.

## Focus areas

- compiled asset catalog dominance
- duplicate resources across the main bundle or extensions
- large localization payloads
- oversized fonts, media, databases, and nib/storyboard outputs

## Guardrails

- Do not suggest lossy asset changes as automatic fixes.
- Treat resource deduplication across targets as advisory unless the evidence is extremely clear.
