# Writing Plans

Use this for any non-trivial ticket before implementation starts.

## Goal

Break work into small, file-scoped tasks that can be executed and verified
without vague handoffs.

## Workflow

1. Read the ticket and extract acceptance criteria verbatim.
2. Identify the target project key and task id.
3. Break the work into narrow tasks.
4. For each task, specify:
   role, reads, writes, acceptance, and the next verification step.
5. Insert compiler/test/review/QA gates as explicit tasks, not implied steps.

## Rules

- A task should touch one concern when possible.
- If a task edits many files, split it.
- Every plan must end with verification and QA.
- If a change cannot be verified, the plan is incomplete.
