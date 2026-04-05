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

## How to Use This Skill

### Codex / repo-native skill runners

Clone the repo, open it in your coding agent, and invoke the orchestrator-style workflow from the skill files under `skills/`. This is the most complete and best-supported path.

Typical entry points:

- `skills/xcode-size-orchestrator/SKILL.md`
- `skills/xcode-size-benchmark/SKILL.md`
- `skills/xcode-size-fixer/SKILL.md`

### `npx`

The repository now includes a small Node CLI wrapper that delegates to the bundled Python scripts.

Use it locally from a clone:

```bash
npx --yes . --help
npx --yes . measure --workspace-root /path/to/app --project MyApp.xcodeproj --scheme MyApp --configuration Release --export-ipa
```

After publishing this package to npm, the public form becomes:

```bash
npx xcode-release-size-optimization-agent-skill --help
```

### Homebrew

Homebrew now requires third-party formulae to live in a tap, so the supported install path is through the dedicated tap repo at `danglingP0inter/homebrew-tap`.

```bash
brew tap danglingP0inter/tap
brew install --HEAD danglingP0inter/tap/xcode-release-size-optimization-agent-skill
```

The formula source is also kept in this repo under `Formula/xcode-release-size-optimization-agent-skill.rb` and mirrored into the tap. The tap currently tracks `HEAD` from `main`. A stable bottled formula should be added once the project starts shipping tagged releases.

### GitHub Copilot

Open the repository in an environment that supports repo instructions and project skills. Copilot-facing discovery files live under `.github/skills/` and `.github/copilot-instructions.md`, so prompts about IPA size, archive size, stripping, thinning, or release-size optimization are more likely to route correctly.

### Claude Code / Claude-style agents

Open the repository directly in Claude Code or another Claude-style agent that reads `CLAUDE.md` and `.claude/skills/`. This repo is Claude-friendly today, but it is not packaged as a separate installable Claude Code plugin.

### Cursor

Open the repository in Cursor. The rule file under `.cursor/rules/` gives Cursor a focused operating procedure for release-size analysis and approval-gated fixes.

### Manual script usage

You can also run the deterministic analysis scripts directly:

```bash
python3 scripts/measure_release.py \
  --workspace-root /path/to/app \
  --project MyApp.xcodeproj \
  --scheme MyApp \
  --configuration Release \
  --export-ipa

python3 scripts/render_report.py \
  --artifacts-dir /path/to/app/.size-analysis \
  --output /path/to/app/.size-analysis/size-optimization-plan.md
```

The primary report is generated at `.size-analysis/size-optimization-plan.md`.

### Claude plugin packaging

Not yet. The repository is Claude-friendly, but it is not packaged as a standalone Claude Code plugin. If Claude formalizes a stable public plugin packaging format for local repositories, this repo can be wrapped into that format later without changing the core workflow.

## Notes

- First-class support targets iOS apps built with Xcode-native project settings and Swift Package Manager.
- CocoaPods, Carthage, and unusual multi-target packaging are detected and called out as limited-support cases instead of being silently ignored.
- Release-size fixes and export-oriented optimizations are intentionally scoped to `Release`, not `Debug`.

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
