# Sushi Company — AI Software Company on Your Mac

A multi-agent software company built entirely on universal agent profiles and customizable CLI drivers. You file tickets; the CEO agent plans, delegates to specialist agents, iterates until QA approves, and ships the deliverable.

## Org chart

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

## File layout

```
~/.sushi/                     # The agent configuration home directory
  agents/                     # The universal agent profiles (Markdown + YAML frontmatter)
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
  bin/
    ticket                    # Create a new ticket, prints path
    ship                      # Run the CEO on a ticket, company executes it end-to-end
    sushi                     # Query the CEO for status reports / ad-hoc requests
    models                    # View/configure the role-to-model routing table
    model-for                 # Model resolution helper
    status-board              # Tracks multi-agent running processes
    cost-report               # Parses run logs to calculate total token spend
  tickets/                    # T-0001.md, T-0002.md...
  projects/                   # Per-ticket working dirs (code deliverables live here)
  logs/                       # Per-ticket delegation trail written by the CEO
  docs/                       # This architectural reference folder
```

## Usage

### 1. File a ticket

```bash
ticket "Short title" "Description with acceptance criteria"
# Prints: ~/.sushi/company-state/tickets/T-0003.md
```

Or with no args to open an editor on a template:

```bash
ticket
```

### 2. Ship it

```bash
ship T-0003
# or by path
ship ~/.sushi/company-state/tickets/T-0003.md
# or one-shot: create + ship
ship --new "Add dark mode toggle" "Description..."
```

The CEO agent takes over from there. It:

1. Reads the ticket.
2. Creates `~/.sushi/company-state/projects/T-0003/` as the working dir.
3. Writes a plan to `~/.sushi/company-state/logs/T-0003.md`.
4. Calls `cto` to break the ticket into tasks.
5. Delegates each task to the right specialist (`backend`, `frontend`, `systems`, etc.).
6. Runs `compiler` after implementation to confirm it builds clean.
7. Calls `unit-test` and `bdd-test` to add tests.
8. Runs `code-reviewer` on the diff.
9. Runs `qa` — only their `APPROVED` marks the ticket `DONE`.

### Add to PATH (optional, recommended)

```bash
echo 'export PATH="$HOME/workspace/sushi-company/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
# then:
ticket "..." "..."
ship T-0003
```

---

## Switching CLI Engines

By default, the company runs using the `copilot` CLI isolated under `~/.sushi`. You can effortlessly swap drivers to other AI engines by exporting the `SUSHI_CLI` environment variable:

```bash
# Swaps to standard Gemini-based / Antigravity CLI engine
export SUSHI_CLI="agy"

# Swaps to Claude CLI engine
export SUSHI_CLI="claude-cli"
```

---

## Editing agent behavior

Each agent is a plain Markdown file in `~/.sushi/agents/`. Edit the prompt, save, done — next invocation picks it up.

Add a brand new specialist by creating `~/.sushi/agents/<name>.agent.md` with YAML frontmatter (`name`, `description`, `tools`) and a Markdown body describing the role. Then add it to the CEO's specialist table (in `copilot-instructions.md`) so the CEO knows to route to it.

---

## Cost notes

Every CLI request is $\ge 1$ premium request. A typical ticket (plan → 2–4 impl tasks → compile → test → review → QA) uses ~10–15 premium requests. Set expectations accordingly.
