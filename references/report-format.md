# Report Format

The primary report lives at `.size-analysis/size-optimization-plan.md`.

## Required sections

1. Project context and assumptions
2. Compatibility status
3. Baseline measurements
4. Size attribution summary
5. Build and export settings
6. Prioritized recommendations
7. Approval checklist
8. Verification summary
9. Unsupported or partially supported findings

## Recommendation template

Each recommendation should include:

- `ID`
- `Title`
- `Area`: binary, resources, dependencies, or structure
- `Impact`
- `Risk`: low, medium, or high
- `Confidence`
- `Fixer eligible`: yes or no
- `Evidence`
- `Why it matters`
- `Approval`: unchecked by default for analysis runs

## Writing guidance

- Rank by expected bytes saved, then confidence, then risk.
- Prefer concrete evidence over generic guidance.
- Call out uncertainty directly when attribution is partial.
- Keep the report shareable in pull requests and issue threads.
