# Brainstorming

Use this before coding when the problem is ambiguous, has multiple valid
architectures, or could cause expensive rework.

## Goal

Produce a short design note that narrows options and gives the implementation a
 clear direction.

## Workflow

1. Restate the user goal in one sentence.
2. List the real constraints:
   paths, stack, deployment, tests, performance, backward compatibility.
3. Generate 2-4 viable approaches.
4. For each approach, state:
   complexity, risk, likely failure mode, and migration cost.
5. Choose one approach and say why it wins.
6. Convert the choice into the first concrete implementation tasks.

## Output

- One short summary paragraph.
- A flat list of options with tradeoffs.
- A single recommended path.

Do not start coding until the recommendation is explicit.
