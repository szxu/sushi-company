# Sushi Company TODO

Status: public vanilla 0.2.0 ready
Updated: 2026-05-29

## Completed For Public Sharing

- [x] Runtime state lives outside the framework repo in `SUSHI_STATE_DIR`.
- [x] Runtime state defaults to `~/.sushi/company-state`.
- [x] Vanilla repo excludes private tickets, logs, projects, and build artifacts.
- [x] `bin/export-vanilla` creates a sanitized shareable folder.
- [x] `bin/share-doctor` blocks private state, large files, and unsafe artifacts.
- [x] `bin/doctor` validates local install health.
- [x] `make test` runs a smoke suite.
- [x] Project-based task IDs use four-letter keys, e.g. `SUSH-0001`.
- [x] `bin/project` creates, lists, and selects project keys.
- [x] Engine switching supports Copilot, Claude, Gemini, Antigravity, OpenCode, Cursor, and Windsurf.
- [x] README highlights the core selling point: switch away from an expensive or weak coding tool without losing the company workflow.
- [x] Versioning and changelog added.
- [x] Ticket templates added for web apps, CLI tools, bug fixes, and research spikes.

## Still Useful Later

- [ ] Add a richer sample app under `examples/`.
- [ ] Add real integration tests for the browser GUI.
- [ ] Add status reconciliation between task files, logs, and status board.
- [ ] Add optional hosted docs site.
- [ ] Add shell completions for `engines`, `project`, `ticket`, and `ship`.
