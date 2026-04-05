## Quick orientation for code-writing agents

This repository contains a suite of agent workflows for measuring and reducing iOS Release build size. These instructions are intentionally short and prescriptive so external agents can route into the right skill quickly.

Primary entry points
- External Copilot-style skill: `.github/skills/xcode-release-size-optimization/SKILL.md`
- Canonical internal workflow: `skills/xcode-size-orchestrator/SKILL.md`
- General repo instructions: `AGENTS.md`

When this repo is relevant
- Reduce iOS app size
- Optimize Release build size
- Shrink IPA before App Store submission
- Investigate archive bloat
- Review stripping, symbol payloads, or app thinning

Non-negotiable rules
- Release-only. Do not optimize `Debug`.
- Analysis is read-only.
- All evidence goes into `.size-analysis/`.
- Only apply approved low-risk fixes.
- Treat symbol/debug-info changes as at least medium risk unless clearly safe.

Authority files
- `skills/xcode-size-orchestrator/SKILL.md`
- `references/compatibility.md`
- `references/fixer-scope.md`
- `references/measurement-contract.md`
- `references/report-format.md`
- `references/size-checks.md`

Core commands
- Baseline: `python3 scripts/measure_release.py --workspace-root . --project <path>.xcodeproj --scheme <scheme> --configuration Release --export-ipa`
- Binary analysis: `python3 scripts/analyze_macho.py <app-path> --output .size-analysis/top_binaries.json`
- Resource analysis: `python3 scripts/analyze_resources.py <app-path> --output .size-analysis/top_resources.json`
- SwiftPM analysis: `python3 scripts/analyze_swiftpm.py <workspace-root> --output .size-analysis/swiftpm-summary.json`
- Render report: `python3 scripts/render_report.py`
- Approved low-risk build-setting fixes: `python3 scripts/apply_low_risk_size_fixes.py --pbxproj <project.pbxproj> --approved-json <json>`

Notes on discovery
- GitHub Copilot can auto-discover project skills under `.github/skills/` or `.claude/skills/` based on the skill description.
- Other agents may use `AGENTS.md`, `CLAUDE.md`, or `.cursor/rules/*.mdc` instead.
- There is no universal auto-reference mechanism across all AI tools, so this repo includes multiple entry points on purpose.
