# Sushi Company

This is the shareable framework repo. Keep private runtime state outside the
repo by using `SUSHI_STATE_DIR`, which defaults to `~/.sushi/company-state`.

Use the repo-local skills when the task matches them:

- [brainstorming](/Users/douglas/workspace/sushi-company-vanilla/skills/core/brainstorming/SKILL.md)
- [writing-plans](/Users/douglas/workspace/sushi-company-vanilla/skills/core/writing-plans/SKILL.md)
- [test-driven-development](/Users/douglas/workspace/sushi-company-vanilla/skills/core/test-driven-development/SKILL.md)
- [systematic-debugging](/Users/douglas/workspace/sushi-company-vanilla/skills/core/systematic-debugging/SKILL.md)
- [requesting-code-review](/Users/douglas/workspace/sushi-company-vanilla/skills/core/requesting-code-review/SKILL.md)
- [verification-before-completion](/Users/douglas/workspace/sushi-company-vanilla/skills/core/verification-before-completion/SKILL.md)

Default expectations:

- Plan before non-trivial implementation.
- Prefer a failing test before a fix when the behavior is testable.
- Debug by reproducing and isolating root cause, not by guessing.
- Verify acceptance criteria before claiming completion.

Do not commit real tickets, project workdirs, logs, build artifacts, PID files,
or local CLI state. Use `bin/share-doctor <export-dir>` before publishing.
