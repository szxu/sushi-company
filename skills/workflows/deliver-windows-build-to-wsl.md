# Workflow: Deliver Windows build to Douglas's WSL for testing

**When**: every time a new `win-unpacked/` artifact is produced for any ticket. Do this BEFORE telling Douglas the build is ready.

## Steps

1. Confirm artifact exists locally:
   `$SUSHI_STATE_DIR/projects/<TICKET>/artifacts/win-unpacked/`
   - Must contain `Dota 2 Ability Draft Plus.exe` and `resources/build-info.json`.

2. Load WSL creds:
   ```bash
   set -a; source ~/.hermes/secrets/windows-wsl.env; set +a
   ```

3. Pick a uniquely-named remote folder so prior builds aren't overwritten:
   ```bash
   SHORT_SHA=$(node -e "console.log(require('PROJ/artifacts/win-unpacked/resources/build-info.json').gitSha.slice(0,7))")
   REMOTE=/home/treeboy/workspace/ability-draft-plus/dist/win-unpacked-${TICKET}-${SHORT_SHA}
   ```

4. Rsync (faster than scp for re-deliveries):
   ```bash
   sshpass -p "$WSL_SSH_PASS" rsync -az --progress \
     -e "ssh -o StrictHostKeyChecking=accept-new -p $WSL_SSH_PORT" \
     "$SUSHI_STATE_DIR/projects/$TICKET/artifacts/win-unpacked/" \
     "$WSL_SSH_USER@$WSL_SSH_HOST:$REMOTE/"
   ```
   NOTE: macOS ships openrsync — do NOT use `--info=progress2` (only GNU rsync supports it). Use `--progress` instead.
   If you want a clean dest first: `ssh ... "rm -rf '$REMOTE'/* && mkdir -p '$REMOTE'"` before rsync.
   Fallback if rsync missing: `scp -r -P $WSL_SSH_PORT ... "$WSL_SSH_USER@$WSL_SSH_HOST:$REMOTE"`.

5. Verify on the remote side:
   ```bash
   sshpass -p "$WSL_SSH_PASS" ssh -p $WSL_SSH_PORT $WSL_SSH_USER@$WSL_SSH_HOST \
     "ls '$REMOTE/Dota 2 Ability Draft Plus.exe' && cat '$REMOTE/resources/build-info.json'"
   ```

6. Tell Douglas:
   - Remote path (he can `\\wsl$\...` or scp out to Windows)
   - The buildId from build-info.json so he can confirm the right binary
   - Any caveats (e.g. delete `%APPDATA%\ability-draft-plus` if testing a window-bounds fix)

## Notes
- Don't ship a build that lacks `resources/build-info.json` — that means write-build-info.mjs didn't run; rebuild instead.
- Don't reuse remote folder names across tickets; Douglas may want to A/B compare.
- If rsync fails partway, retry — it resumes.
