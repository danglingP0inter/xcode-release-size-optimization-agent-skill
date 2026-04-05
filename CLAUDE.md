# Claude Project Instructions

This repository provides an evidence-first workflow for iOS Release build size optimization.

Use this repository's workflow when the user asks to:
- reduce iOS app size
- investigate IPA or archive bloat
- optimize Release packaging before App Store submission
- evaluate binary stripping, symbol payloads, or app thinning

## What to do

1. Start with `skills/xcode-size-orchestrator/SKILL.md`.
2. Keep analysis read-only.
3. Produce artifacts in `.size-analysis/`.
4. Generate `size-optimization-plan.md` before proposing code changes.
5. Only apply explicitly approved low-risk fixes.
6. Re-measure after any approved changes.

## Constraints

- Release-only. Never optimize `Debug` in this repo's workflow.
- Treat symbol/debug-info changes as at least medium risk unless clearly safe.
- Treat thinning as optional and context-dependent; for `app-store` exports, explain that local thinning is not equivalent to App Store delivery behavior.
