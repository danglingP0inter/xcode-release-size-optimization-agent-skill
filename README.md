# Xcode Release Size Optimization Agent Skill

Open-source agent skills for analyzing and reducing iOS release build size before App Store submission.

## Included skills

- `xcode-size-orchestrator`
- `xcode-size-benchmark`
- `xcode-binary-size-analyzer`
- `xcode-resource-size-analyzer`
- `xcode-dependency-size-analyzer`
- `xcode-size-fixer`

## Workflow

1. Run the orchestrator to collect a release-size baseline in `.size-analysis/`.
2. Review the generated `size-optimization-plan.md`.
3. Approve only the items you want applied.
4. Use the fixer to implement approved low-risk changes and re-measure.

## Notes

- First-class support targets iOS apps built with Xcode-native project settings and Swift Package Manager.
- CocoaPods, Carthage, and unusual multi-target packaging are detected and called out as limited-support cases instead of being silently ignored.

## External Agent Support

This repo is set up to be discoverable by multiple AI coding agents:

- GitHub Copilot: `.github/skills/xcode-release-size-optimization/SKILL.md`
- Claude-style agents: `.claude/skills/xcode-release-size-optimization/SKILL.md` and `CLAUDE.md`
- Cursor-style agents: `.cursor/rules/xcode-release-size-optimization.mdc`
- General agents: `AGENTS.md`

There is no single universal auto-load standard across all agent products, but these files make the repo much more likely to be auto-routed correctly when a prompt mentions iOS app size, IPA size, archive bloat, stripping, thinning, or App Store submission size optimization.

## Example App

A small validation project lives in `examples/SizeValidationApp/` so agents and maintainers can test the workflow against a real iOS app.

Generated build output such as `.size-analysis/`, `DerivedData/`, `.xcarchive`, and `.ipa` files is intentionally ignored and should not be committed.

