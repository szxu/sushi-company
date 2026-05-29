# Systematic Debugging

Use this when a bug is unclear, intermittent, or crosses layers.

## Goal

Reduce guesswork. Turn the bug into a bounded reproduction and isolate the
actual failing assumption.

## Workflow

1. Write the shortest known reproduction.
2. Define expected behavior vs actual behavior.
3. Narrow the failing layer:
   input, parsing, state, business logic, rendering, integration, environment.
4. Add temporary instrumentation only where the branch decision is unclear.
5. State the root cause in one sentence before patching.
6. Add a regression test.
7. Remove temporary instrumentation unless it is genuinely useful logging.

## Rules

- Do not patch based on intuition alone.
- Reproduce first, then isolate, then fix, then prove.
