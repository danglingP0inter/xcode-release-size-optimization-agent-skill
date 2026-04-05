# Release Build Size Checks

This catalog is the policy layer for recommendations. Every finding should map back to one of these checks.

## Binary and linker checks

### `BIN001` Dead code stripping
- Measure: release linker settings and final executable size
- Detect: `DEAD_CODE_STRIPPING` disabled or ineffective
- Why it matters: unused code remains in the shipping binary
- Confidence: high
- Risk: low
- Fixer eligible: yes

### `BIN002` Release optimization level
- Measure: release build settings for Swift and Clang
- Detect: size-hostile optimization levels in release
- Why it matters: binary size can grow unnecessarily
- Confidence: medium
- Risk: medium
- Fixer eligible: yes, only with explicit approval

### `BIN003` Symbol stripping and debug payloads
- Measure: executable, dSYM, and export-related symbol settings
- Detect: symbols or debug payloads shipped unintentionally, or release stripping settings disabled
- Why it matters: exported artifacts become larger and symbol handling gets muddled
- Confidence: medium
- Risk: medium
- Fixer eligible: yes, only for clearly safe packaging toggles

### `BIN004` Oversized embedded frameworks
- Measure: framework and XCFramework footprint
- Detect: large frameworks dominating bundle size
- Why it matters: third-party binaries are often the fastest route to size wins
- Confidence: high
- Risk: advisory
- Fixer eligible: no

### `BIN005` Architecture slice issues
- Measure: lipo-reported slices for app and frameworks
- Detect: unexpected or duplicate architectures in shipping content
- Why it matters: extra slices inflate artifacts immediately
- Confidence: high
- Risk: medium
- Fixer eligible: no

### `BIN006` Export thinning configuration
- Measure: export options and resulting IPA generation mode
- Detect: explicit thinning requests, or local packaged IPA fallback that cannot represent thinning
- Why it matters: thinning can change exported artifact size, but App Store submissions use Apple-managed processing
- Confidence: medium
- Risk: low
- Fixer eligible: no

## Resource and asset checks

### `RES001` Oversized asset catalogs
- Measure: compiled asset catalog footprint and top image families
- Detect: dominant image sets or raster-heavy catalogs
- Why it matters: assets often outweigh code in consumer apps
- Confidence: high
- Risk: advisory
- Fixer eligible: no

### `RES002` Duplicate resources
- Measure: file hashes and duplicate names across bundles
- Detect: identical payloads copied into multiple targets or folders
- Why it matters: duplicated bytes ship multiple times
- Confidence: high
- Risk: medium
- Fixer eligible: no

### `RES003` Localization payload bloat
- Measure: `.lproj` directories and localized assets
- Detect: very large locale payloads or debug/demo strings bundled in release
- Why it matters: localization can scale size unexpectedly
- Confidence: medium
- Risk: advisory
- Fixer eligible: no

### `RES004` Large bundled data, fonts, and nibs
- Measure: large non-image resource categories
- Detect: top offenders in fonts, JSON, databases, media, storyboards, xibs
- Why it matters: non-code files are easy to miss in bundle audits
- Confidence: high
- Risk: low to medium
- Fixer eligible: no

## Dependency checks

### `DEP001` Heavy SwiftPM packages
- Measure: package resolution and bundled framework/resource output
- Detect: packages with disproportionate shipped footprint
- Why it matters: package convenience can hide shipping cost
- Confidence: medium
- Risk: advisory
- Fixer eligible: no

### `DEP002` Transitive package bloat
- Measure: package graph depth and packaged outputs
- Detect: indirect dependencies contributing large binaries/resources
- Why it matters: transitive dependencies are often low-visibility size regressions
- Confidence: low to medium
- Risk: advisory
- Fixer eligible: no

### `DEP003` Debug or demo resources leaking into release
- Measure: packaged files with known debug/demo/test naming signals
- Detect: release bundles containing non-shipping resources
- Why it matters: this is a common low-risk cleanup opportunity
- Confidence: medium
- Risk: low
- Fixer eligible: yes when clearly scoped

## Structure and shipping checks

### `STR001` App and extension duplication
- Measure: shared filenames and hashes across app/plug-in bundles
- Detect: repeated resources or frameworks
- Why it matters: multi-target apps can pay for the same bytes repeatedly
- Confidence: medium
- Risk: medium
- Fixer eligible: no

### `STR002` Unsupported packaging path
- Measure: dependency and project layout signals
- Detect: CocoaPods, Carthage, or custom packaging
- Why it matters: protects recommendation quality
- Confidence: high
- Risk: none
- Fixer eligible: no
