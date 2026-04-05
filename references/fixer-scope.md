# Fixer Scope

The fixer is intentionally conservative in v1.

## Eligible changes

- low-risk build-setting corrections in release configurations
- approved symbol-stripping toggles such as `COPY_PHASE_STRIP=YES` and `STRIP_INSTALLED_PRODUCT=YES`
- excluding known debug-only assets or resources from release packaging
- safe stripping or packaging toggles that do not change runtime behavior
- project-file edits that are directly traceable to an approved item in the report

## Advisory-only items

- source-level refactors
- dependency replacements
- image recompression or asset format conversion
- target restructuring or resource deduplication across architectural boundaries
- changes that alter symbolication guarantees without explicit user approval

## Required fixer workflow

1. Read `.size-analysis/size-optimization-plan.md`.
2. Apply only recommendations explicitly marked approved.
3. Record every implemented item in the verification section.
4. Re-run baseline measurement and generate `comparison.json`.
5. Stop if the project no longer builds or archive generation fails.
