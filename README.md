# 🍣 Sushi Company — Universal Multi-Agent AI Software Company

A universal, CLI-agnostic, and AI-friendly software company framework built to run entirely inside your terminal or integrate directly with your IDE assistant. You file tickets; the CEO agent plans, delegates to specialist agents, compiles, tests, performs peer code reviews, and iterates until the QA agent approves the build and ships the deliverable.

```
          Douglas (you)
               │
            tickets
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

## 🚀 Key Features

*   **Universal CLI Driver (`$SUSHI_CLI`)**: Works with any terminal AI CLI engine. Defaults to GitHub Copilot CLI, but easily adapts to other engines.
*   **Environment Encapsulation**: Runs inside an isolated configuration home directory (`~/.sushi/`) to prevent clashing with your global CLI settings.
*   **IDE-Assistant Friendly**: Integrates seamlessly with advanced coding assistants (such as Antigravity/`agy`) via local workspace symlinks (`.gemini/agents` and `.agy/agents`).
*   **10 Specialized AI Specialists**: Includes complete out-of-the-box profiles for a CTO, UI/UX Designer, Frontend dev, Backend dev, Systems/DevOps dev, Unit-tester, BDD-tester, Compiler gatekeeper, Peer Code Reviewer, and QA engineer.

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
    ticket                    # Tool to create a new development ticket
    ship                      # Executes a ticket end-to-end via the CEO
    sushi                     # Queries the CEO for status reports / ad-hoc requests
    models                    # Audits and sets the role-to-model routing policy
    model-for                 # Backend model-resolution helper
    status-board              # Tracks multi-agent running processes
    cost-report               # Parses run logs to calculate total token spend
  config/
    models.json               # Centralized model allocation policy
  tickets/                    # Private runtime state; defaults outside repo
  projects/                   # Private per-ticket working directories
  logs/                       # Private run logs and delegation trails
  docs/                       # Detailed architectural references
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

## ⚡ How to Switch CLI Engines

By default, the scripts execute using the `copilot` CLI engine under the isolated home directory `$HOME/.sushi`. You can effortlessly swap drivers to other AI engines by exporting the `SUSHI_CLI` environment variable:

```bash
# Default (GitHub Copilot CLI)
export SUSHI_CLI="copilot"

# Swap to custom Claude CLI engine
export SUSHI_CLI="claude-cli"

# Swap to custom Gemini / Antigravity CLI engine
export SUSHI_CLI="agy"
```

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

### 1. File a Ticket
Create a new ticket from the command line:
```bash
ticket "Add a /health API endpoint" "Implement GET /health returning status: ok"
# Prints path: ~/.sushi/company-state/tickets/T-0003.md
```

### 2. Ship the Ticket
Hand the ticket to the CEO to execute:
```bash
ship T-0003
```

The CEO will immediately:
1. Parse the ticket and create `projects/T-0003/` as the working directory.
2. Outline a delegation plan in `logs/T-0003.md`.
3. Invoke the **`cto`** to generate a JSON step-by-step task execution plan.
4. Execute the tasks in sequence using the designated **`backend`** or **`frontend`** specialists.
5. Invoke the **`compiler`** to ensure the build compiles and lints with zero errors.
6. Call the **`unit-test`** and **`bdd-test`** agents to write and execute isolated test suites.
7. Invoke the **`code-reviewer`** to analyze the git diff.
8. Call **`qa`** for final verification of the acceptance criteria. If approved, the ticket is marked `DONE` and shipped!
