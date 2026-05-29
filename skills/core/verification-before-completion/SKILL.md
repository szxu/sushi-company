# Verification Before Completion

Use this at the end of every non-trivial task.

## Goal

Do not confuse "code was written" with "task is done".

## Workflow

1. Re-read the acceptance criteria.
2. Run the narrowest relevant tests.
3. Run the broader build/lint/typecheck gate if the change touches shared code.
4. Check the artifact the user will actually experience:
   CLI output, API response, GUI state, export contents, file layout.
5. Record any unverified assumption explicitly.

## Completion Rule

A task is complete only when:

- acceptance criteria were checked,
- tests or equivalent verification passed,
- review passed or no review blockers remain,
- remaining risk is stated plainly.
