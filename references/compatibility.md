# Compatibility and Guardrails

## First-class support

- iOS apps built with Xcode-native project or workspace settings
- Swift Package Manager dependencies
- `.app`, `.ipa`, and `.xcarchive` inspection on macOS hosts with Xcode command line tools

## Detected limited-support cases

- CocoaPods (`Podfile`, `Pods/`, or `Pods.xcodeproj`)
- Carthage (`Cartfile`, `Carthage/`)
- custom shell packaging steps that bypass standard export flows
- multiple embedded targets with nonstandard resource routing

When limited support is detected, the skills should:

1. Continue any measurements that remain reliable.
2. Add a warning to `.size-analysis/compatibility.json`.
3. Surface the warning in the markdown plan.
4. Avoid overconfident recommendations that depend on unsupported packaging assumptions.

## Hard safety rules

- Analysis skills must not modify project files.
- The fixer must only implement explicitly approved, low-risk changes.
- Recommendations that may affect runtime behavior, crash symbolication, or debugging quality must be labeled as medium or high risk.
- If the workspace does not produce a release artifact, the suite should report the missing prerequisite rather than guessing.
