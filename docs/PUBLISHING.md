# Publishing Sushi Company

Sushi Company has two layers:

1. Framework code: the shareable repo containing `bin/`, `config/`, `docs/`,
   `gui/`, `skills/`, templates, and launch scripts.
2. Runtime state: private tickets, projects, logs, and status history.

Runtime state defaults to:

```bash
~/.sushi/company-state
```

Override it with:

```bash
export SUSHI_STATE_DIR=/path/to/private/state
```

## Local migration

To copy existing repo-local state into the private state directory:

```bash
bin/sushi-migrate-state --copy
```

Review the result, then optionally move the original folders:

```bash
bin/sushi-migrate-state --move
```

The migration command never rewrites Git history.

## Vanilla export

Create a sanitized framework-only folder:

```bash
bin/export-vanilla ~/workspace/sushi-company-vanilla
```

The export includes framework files and templates only. It excludes private
`tickets/`, `projects/`, `logs/`, `STATUS.md`, `.git/`, and known build
artifacts.

Before publishing, run:

```bash
bin/share-doctor ~/workspace/sushi-company-vanilla
```

## Fresh public repo

The safest publishing path is a fresh Git repo from the vanilla export:

```bash
cd ~/workspace/sushi-company-vanilla
git init
git add .
git commit -m "Initial public Sushi Company framework"
```

This avoids pushing private history or large artifacts from a working local
company repo.

## What belongs in Git

- Framework scripts
- Agent templates
- GUI source
- Documentation
- Example tickets and tiny sample projects
- Configuration templates

## What stays private

- Real tickets
- Project workdirs
- Delegation logs
- Run logs
- PID files
- Windows builds and app artifacts
- Any source tree or artifact belonging to a user's personal projects
