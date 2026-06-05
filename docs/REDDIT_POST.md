# Reddit Post Draft: Sushi Company

Title options:

1. I built Sushi Company: a tiny AI software company framework for switching coding tools without losing your workflow
2. I made a vanilla multi-agent coding workflow that lets you switch from Claude/Codex/Cursor/OpenCode/etc.
3. Sushi Company: project tasks, specialist agents, engine switching, and UT/BDD gates in one shareable repo

Post:

I built **Sushi Company**, a portable multi-agent software company framework for vibe coders who want to switch coding tools without losing their workflow.

The main idea: if one coding tool gets too expensive, too slow, or just not smart enough for a task, you can switch engines and keep the same project/task state, specialist roles, model routing, logs, and QA gates.

Supported engine profiles currently include:

- GitHub Copilot CLI
- Claude CLI
- Gemini CLI
- OpenCode
- Cursor
- Windsurf
- OpenAI Codex CLI
- Aider
- Continue
- Goose
- Cline
- JetBrains Junie
- Zed AI
- Tabby
- Kilo Code

What it does:

- Creates Jira-style project task IDs like `DEMO-0001` or `SUSH-0001`
- Keeps private runtime state outside the repo, so the vanilla framework can be shared safely
- Has a Web UI for projects, tasks by project, engine switching, models, logs, and doctor checks
- Has specialist agent roles like CEO, CTO, frontend, backend, systems, unit-test, BDD-test, compiler, code-reviewer, and QA
- Has two required gates: unit tests and browser BDD tests
- Has a clean vanilla Linux BDD gate that verifies the public export works on a fresh Linux system with one `DEMO` task

Why I made it:

I wanted a practical way to avoid tool lock-in. Sometimes Claude is strong but expensive. Sometimes Copilot is already available through a plan. Sometimes Codex, Aider, Cursor, OpenCode, or another tool fits the current job better. Sushi is meant to keep the company workflow stable while the active coding engine can change.

The vanilla repo is designed to be shareable:

- No private tickets
- No private project folders
- No logs or build artifacts
- No large files
- Private state defaults to `~/.sushi/company-state`

Screenshots attached:

- `docs/reddit-assets/01-overview-command-center.png` — Overview / command center
- `docs/reddit-assets/02-projects-demo.png` — Projects page with a clean `DEMO` project
- `docs/reddit-assets/03-tasks-by-project-demo.png` — Tasks by Project with `DEMO-0001`
- `docs/reddit-assets/04-engine-switcher.png` — Engine switcher with supported coding tools
- `docs/reddit-assets/05-logs-demo.png` — Logs / terminal output page

GitHub:

https://github.com/szxu/sushi-company

Bug reports / issues:

https://github.com/szxu/sushi-company/issues/new

I would be interested in feedback from people who actively use more than one AI coding tool. The core question is: does this kind of portable project/task/company layer make switching tools less painful?
