# Sushi Company Architecture

Sushi Company is a project-based multi-agent workflow for people who want to
keep their software-company process while switching coding engines freely.

## Org Chart

```
          You
           |
     project tasks
           |
           v
          CEO  -> cto, frontend, backend, systems
           |  -> unit-test, bdd-test, compiler
           v  -> code-reviewer, qa
         DONE only after QA approves
```

## Runtime Layout

Framework files stay in the cloned repo. Private state lives in
`SUSHI_STATE_DIR`, defaulting to `~/.sushi/company-state`.

```
~/.sushi/company-state/
  current-project
  projects/
    SUSH/
      project.json
      tickets/
        SUSH-0001.md
      work/
        SUSH-0001/
      logs/
        SUSH-0001.md
        SUSH-0001.run.log
  STATUS.md
```

## Commands

```bash
engines list
engines use copilot
engines use claude
engines use opencode
engines use cursor
engines use windsurf

project create "Sushi Company" SUSH
project use SUSH

ticket "Short title" "Description with acceptance criteria"
ship SUSH-0001
```

## Engine Switching

The active engine is stored in `~/.sushi/active-engine`. `sushi-paths` resolves
that engine to the command in `config/engines.json`, so new runs use the selected
tool without changing project state or tickets.

Supported profiles:

- Copilot
- Claude
- Gemini
- Antigravity / Agy
- OpenCode
- Cursor
- Windsurf

## Quality Gates

The CEO workflow remains the same across engines:

1. Plan.
2. Delegate implementation.
3. Compile/lint.
4. Add unit and acceptance tests.
5. Review.
6. QA.
7. Mark done only after QA approves.
