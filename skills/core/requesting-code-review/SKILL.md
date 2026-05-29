# Requesting Code Review

Use this before a task is considered ready.

## Goal

Force an explicit review pass for correctness, security, maintainability, and
test quality.

## Review Checklist

1. Does the code satisfy the ticket as written?
2. Are there missing edge cases or regressions?
3. Is there any obvious security or data-loss risk?
4. Are the tests meaningful, or are they only checking the happy path?
5. Is the implementation simpler than the problem requires?

## Output

- `VERDICT: APPROVE | REQUEST_CHANGES | BLOCK`
- `BLOCKERS:`
- `NITS:`
- `NOTES:`

If there are blockers, do not mark the task done.
