# Sushi Company

![Su Dongpo enjoying sushi with chopsticks](assets/su-dongpo-eating-sushi.png)

Sushi Company is a portable multi-agent software company for vibe coders who do
not want to be locked into one expensive or underperforming coding tool.

If Claude CLI gets too pricey, Copilot feels weak on a task, Cursor is better
for editor work, or OpenCode is the better fit for your budget, Sushi lets you
switch the active engine and keep the same tickets, agents, model policy,
project history, and QA workflow.

```
          You
               │
       project tasks
               │
               ▼
          ┌─────────┐
          │   CEO   │  orchestrator — only agent allowed to spawn others
          └────┬────┘
               │ (runs: $SUSHI_CLI --agent=<role>)
   ┌───────────┼───────────┬───────────┬─────────┬──────────┐
   ▼           ▼           ▼           ▼         ▼          ▼
  cto      frontend     backend     systems  unit-test   bdd-test
                                                            │
                                      ┌──────────┬──────────┤
                                      ▼          ▼          ▼
                                   compiler  code-reviewer  qa  ◀── final gate
```

---

## Why Sushi

* **One-click engine switching**: use `engines use copilot`, `engines use claude`,
  `engines use opencode`, `engines use cursor`, `engines use codex`,
  `engines use aider`, `engines use continue`, `engines use goose`,
  `engines use cline`, `engines use junie`, `engines use zed`,
  `engines use tabby`, or `engines use kilo`.
* **Same company, different brain**: switching engines keeps your tickets,
  agents, project state, logs, and model routing intact.
* **Project-based work tracking**: create Jira-style projects with four-letter
  keys and task IDs like `SUSH-0001`.
* **Private state outside Git**: runtime state lives in `~/.sushi/company-state`
  so the framework repo stays shareable.
* **Specialist roles**: CTO, frontend, backend, systems, unit-test, BDD-test,
  compiler, code-reviewer, QA, and UI designer profiles.
* **Workflow skills baked in**: brainstorming, writing plans, TDD, systematic
  debugging, code review, and verification skills are included as repo-local
  `SKILL.md` files inspired by `obra/superpowers`.
* **Two test gates**: `make test` runs the unit gate and browser BDD gate; the
  vanilla Linux BDD gate verifies the public export on a clean system with a
  `DEMO` example task.

---

## 📂 File Layout

```
~/.sushi/                     # Isolated configuration directory
  agents/                     # The 10 universal agent markdown profiles
    cto.agent.md
    ui-designer.agent.md
    frontend.agent.md
    backend.agent.md
    systems.agent.md
    unit-test.agent.md
    bdd-test.agent.md
    compiler.agent.md
    code-reviewer.agent.md
    qa.agent.md
  copilot-instructions.md     # Unified CEO (Sushi) orchestrator persona

~/workspace/sushi-company/    # The company workspace directory
  .gemini/agents -> ~/.sushi/agents/  # IDE symlinks so your IDE assistant
  .agy/agents    -> ~/.sushi/agents/  # can read and use the same agent profiles!
  bin/
    project                   # Manage project keys such as SUSH
    ticket                    # Create project tasks such as SUSH-0001
    ship                      # Executes a ticket end-to-end via the CEO
    sushi                     # Queries the CEO for status reports / ad-hoc requests
    engines                   # One-command coding engine switching
    models                    # Audits and sets the role-to-model routing policy
    model-for                 # Backend model-resolution helper
    status-board              # Tracks multi-agent running processes
    cost-report               # Parses run logs to calculate total token spend
  config/
    models.json               # Centralized model allocation policy
  projects/<KEY>/tickets/     # Private project task files
  projects/<KEY>/work/        # Private per-task working directories
  projects/<KEY>/logs/        # Private project run logs
  docs/                       # Detailed architectural references
  skills/                     # Reusable workflow skills for any coding engine
```

---

## 🛠️ Installation & Setup

1. **Clone the Directory**:
   Clone this repository to your computer (recommended location: `~/workspace/sushi-company/`).

2. **Initialize Configurations**:
   Run the initialization script (or manually copy the template configuration files into your unified home directory):
   ```bash
   mkdir -p "$HOME/.sushi/agents"
   cp config/models.json "$HOME/.sushi/"
   cp -R templates/agents/* "$HOME/.sushi/agents/"
   ```

3. **Add to PATH**:
   Add the `bin` directory to your shell configuration file (e.g. `~/.zshrc` or `~/.bashrc`):
   ```bash
   export PATH="$HOME/workspace/sushi-company/bin:$PATH"
   ```

4. **Verify System Health**:
   Call the CEO by name to request a company status report:
   ```bash
   sushi
   ```

---

## First 10 Minutes

```bash
git clone git@github.com:<you>/sushi-company.git
cd sushi-company
./bin/sushi-init "$PWD"
./bin/doctor
./bin/engines list
./bin/engines use copilot
./bin/project create "Sushi Company" SUSH
./bin/ticket "Add a health check" "GET /health returns ok"
./bin/ship SUSH-0001
```

## Switch Coding Engines

```bash
engines list
engines use claude
engines use opencode
engines use cursor
engines use windsurf
engines use codex
engines use aider
engines use continue
engines use goose
engines use cline
engines use junie
engines use zed
engines use tabby
engines use kilo
```

Sushi links the selected tool's config directory to `~/.sushi` where possible,
then records the active engine in `~/.sushi/active-engine`. New `ship` runs use
that engine automatically through `SUSHI_CLI`.

---

## 📖 Standard Workflow

### Runtime State

Sushi separates shareable framework code from private runtime state. By default,
tickets, project workdirs, logs, and the status board live in:

```bash
~/.sushi/company-state/
```

Override that location with:

```bash
export SUSHI_STATE_DIR=/path/to/private/state
```

This keeps the framework repo safe to publish without personal projects or large
build artifacts. See `docs/PUBLISHING.md` for the vanilla export workflow.

### Skills

Sushi includes repo-local skills so different coding tools can follow the same
high-signal workflow:

- `skills/core/brainstorming/SKILL.md`
- `skills/core/writing-plans/SKILL.md`
- `skills/core/test-driven-development/SKILL.md`
- `skills/core/systematic-debugging/SKILL.md`
- `skills/core/requesting-code-review/SKILL.md`
- `skills/core/verification-before-completion/SKILL.md`

These are the main takeaways adapted from `obra/superpowers`: stronger
pre-coding thinking, stricter test/review behavior, and explicit verification
before a task is called done.

### 1. Create a Project

```bash
project create "Sushi Company" SUSH
project use SUSH
```

### 2. File a Task
Create a new ticket from the command line:
```bash
ticket "Add a /health API endpoint" "Implement GET /health returning status: ok"
# Prints path: ~/.sushi/company-state/projects/SUSH/tickets/SUSH-0001.md
```

### 3. Ship the Task
Hand the ticket to the CEO to execute:
```bash
ship SUSH-0001
```

The CEO will immediately:
1. Parse the task and create `projects/SUSH/work/SUSH-0001/` as the working directory.
2. Outline a delegation plan in `projects/SUSH/logs/SUSH-0001.md`.
3. Invoke the **`cto`** to generate a JSON step-by-step task execution plan.
4. Execute the tasks in sequence using the designated **`backend`** or **`frontend`** specialists.
5. Invoke the **`compiler`** to ensure the build compiles and lints with zero errors.
6. Call the **`unit-test`** and **`bdd-test`** agents to write and execute isolated test suites.
7. Invoke the **`code-reviewer`** to analyze the git diff.
8. Call **`qa`** for final verification of the acceptance criteria. If approved, the ticket is marked `DONE` and shipped!
