# Sushi Company

This is the shareable framework repo. Keep private runtime state outside the
repo by using `SUSHI_STATE_DIR`, which defaults to `~/.sushi/company-state`.

Do not commit real tickets, project workdirs, logs, build artifacts, PID files,
or local CLI state. Use `bin/share-doctor <export-dir>` before publishing.
