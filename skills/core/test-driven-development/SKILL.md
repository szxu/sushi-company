# Test-Driven Development

Use this when adding or fixing behavior that can be isolated in tests.

## Goal

Force the change through a failing test first so implementation stays minimal
and the regression is proven.

## Workflow

1. Identify the exact behavior change.
2. Add or update the smallest test that should fail before the fix.
3. Run that test and confirm failure.
4. Implement the minimum code to pass.
5. Run the narrow test again.
6. Run the broader relevant suite.

## Rules

- Do not add production code before you know the test you need.
- If the test is hard to write, that is a design signal.
- If the change is UI-only, use the narrowest useful level:
  unit, integration, then e2e only if necessary.
