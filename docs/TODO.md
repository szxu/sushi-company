# Sushi Company TODO

Status: planning
Updated: 2026-05-29

## P0: Make the repo safe to share

- [ ] Move personal runtime state out of the repository root.
  - Current problem: `projects/`, `tickets/`, `logs/`, and `STATUS.md` contain Douglas's private work history and are currently under the shareable repo.
  - Target default state directory: `~/.sushi/company-state/`.
  - Target override: `SUSHI_STATE_DIR=/path/to/state`.
  - Desired layout:
    - `~/.sushi/company-state/tickets/`
    - `~/.sushi/company-state/projects/`
    - `~/.sushi/company-state/logs/`
    - `~/.sushi/company-state/STATUS.md`

- [ ] Update all scripts to separate install/code from runtime state.
  - `bin/ticket`: write new tickets to `$SUSHI_STATE_DIR/tickets`.
  - `bin/ship`: read tickets from state, create projects/logs in state, keep repo path as the application install directory.
  - `bin/sushi`: report from state, not repo-local private folders.
  - `bin/status-board`: write to `$SUSHI_STATE_DIR/STATUS.md`.
  - `bin/cost-report`: read from `$SUSHI_STATE_DIR/logs`.
  - `gui/server.py`: read/write tickets, logs, projects, and status from state.

- [ ] Add a migration command for the current local state.
  - Proposed command: `bin/sushi-migrate-state`.
  - Move or copy existing repo-local `tickets/`, `projects/`, `logs/`, and `STATUS.md` into `~/.sushi/company-state/`.
  - Leave placeholders such as `tickets/.gitkeep`, `projects/.gitkeep`, and `logs/.gitkeep` only if keeping empty directories helps onboarding.
  - Print exact paths and never delete source data unless explicitly requested.

- [ ] Add `.gitignore` rules for runtime and build outputs.
  - Ignore `projects/`, `tickets/`, `logs/`, `STATUS.md`, `*.run.log`, `*.pid`, `artifacts/`, `win-unpacked/`, `*.asar`, `*.exe`, `*.so`, `__pycache__/`, `.pytest_cache/`, and egg-info outputs.
  - Keep shareable templates under separate paths such as `templates/tickets/`.

- [ ] Remove private/runtime paths from Git tracking.
  - Use `git rm --cached` for repo-local state paths after migration.
  - Confirm `git status` only shows intended framework files.

- [ ] Produce a clean public Git history.
  - Current repo history contains a large pack around 570MB and personal runtime artifacts.
  - Recommended approach: create a fresh public repo/export from a sanitized tree rather than pushing this existing history.
  - Alternative: rewrite history with `git filter-repo`, then force-push only if this repo is not already shared.

## P0: Vanilla public distribution

- [ ] Create a sanitized shareable export.
  - Proposed folder: `~/workspace/sushi-company-vanilla`.
  - Include framework code only: `bin/`, `config/`, `docs/`, `gui/`, `skills/`, `README.md`, launchers, install/init scripts, and templates.
  - Exclude private state: `tickets/`, `projects/`, `logs/`, `STATUS.md`, local symlink folders, and `.git/`.

- [ ] Add an export script.
  - Proposed command: `bin/export-vanilla`.
  - Copy only allowlisted framework paths into the vanilla folder.
  - Generate empty state placeholders or sample templates.
  - Run a privacy check before declaring the export ready.

- [ ] Add a privacy/shareability checker.
  - Proposed command: `bin/share-doctor`.
  - Fail if export contains:
    - `projects/`
    - real `tickets/`
    - `logs/`
    - `STATUS.md`
    - files over 50MB
    - `.pid`, `.run.log`, `.asar`, `.exe`, `.so`
    - absolute Douglas-only project paths in public docs, except examples clearly marked as examples.

- [ ] Add first-run onboarding for vibe coders.
  - `bin/sushi-init` should create a fresh user state directory.
  - Add `templates/tickets/example.md`.
  - Add a short "First 10 minutes" guide:
    - install
    - choose CLI engine
    - set model policy
    - file first ticket
    - run `ship`
    - open GUI

- [ ] Make the public README describe the product, not Douglas's local company.
  - Explain the state directory model.
  - Explain supported CLI engines.
  - Explain role/model routing.
  - Explain privacy boundaries.
  - Include "what gets committed" vs "what stays local".

## P1: Operational cleanup

- [ ] Normalize ticket status into one source of truth.
  - Decide whether ticket files or logs own canonical status.
  - Add a reconciler that reports disagreements between tickets, logs, queue, and project directories.

- [ ] Fix GUI ticket parsing.
  - Support `# T-0001: Title`.
  - Support `# T-0001 - Title`.
  - Support `# T-0001 -- Title`.
  - Support `# T-0001 — Title`.
  - Support follow-up IDs such as `T-0002-FOLLOWUP-8`.

- [ ] Add `bin/doctor`.
  - Check agent profiles exist.
  - Check symlinks.
  - Check model config.
  - Check stale PID files.
  - Check active jobs.
  - Check malformed tickets.
  - Check GUI port state.
  - Check state directory permissions.

- [ ] Clean stale PID files after confirming no matching process exists.

- [ ] Improve `ship` execution management.
  - Consider managed background CEO runs with log polling and timeout controls.
  - Keep duplicate-run protection.
  - Preserve simple foreground mode as an option if useful.

## P1: Test and release quality

- [ ] Add a root test suite for shell helpers and GUI parsing.
  - Test `model-for`.
  - Test ticket ID generation.
  - Test status-board append/running parsing.
  - Test GUI ticket parser with colon, dash, em dash, and follow-up IDs.

- [ ] Add a release checklist.
  - `bin/doctor` passes.
  - `bin/share-doctor <vanilla-dir>` passes.
  - no files over 50MB.
  - no private tickets/logs/projects.
  - fresh clone install smoke test passes.

- [ ] Add versioning.
  - Add `VERSION`.
  - Add changelog.
  - Add release notes template.

## P2: Product polish

- [ ] Convert remaining hard-coded local paths into resolved workspace/state paths.

- [ ] Add environment documentation for:
  - `SUSHI_HOME`
  - `SUSHI_STATE_DIR`
  - `SUSHI_CLI`
  - `COMPANY_DIR`

- [ ] Add templates for common ticket types.
  - Web app
  - CLI tool
  - Bug fix
  - Windows build
  - Research spike

- [ ] Make model policy friendlier for public users.
  - Default to broadly available models.
  - Keep premium model examples as optional.
  - Document how to run `models list-available`.

- [ ] Add a sample project that is intentionally tiny and non-private.
  - Example: Hello CLI or Todo API.
  - Keep it under `examples/`, not `projects/`.

## Notes from 2026-05-29 review

- Repo size: about 5.0GB.
- Runtime projects size: about 4.4GB.
- Git pack size: about 570MB.
- Tracked private/runtime paths under `projects/`, `logs/`, and `tickets/`: about 16,845 files.
- Large artifacts found under repo-local `projects/`: 119MB `.asar`, 204MB `.exe`, and 301MB `.so` files.
- Preferred publishing strategy: keep this local repo as Douglas's working company, create a fresh sanitized vanilla repo/export for public sharing.
