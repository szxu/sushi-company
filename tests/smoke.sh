#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_STATE="$(mktemp -d /tmp/sushi-vanilla-test.XXXXXX)"
TMP_HOME="$(mktemp -d /tmp/sushi-home-test.XXXXXX)"
EXPORT_DIR=""
SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_STATE" "$TMP_HOME"
  [[ -z "$EXPORT_DIR" ]] || rm -rf "$EXPORT_DIR"
}
trap cleanup EXIT

export SUSHI_STATE_DIR="$TMP_STATE"
export SUSHI_HOME="$TMP_HOME"
export HOME="$TMP_HOME/home"
mkdir -p "$HOME"

"$ROOT/bin/project" create "Sushi Company" SUSH >/tmp/sushi-project.out
grep -q "created project: SUSH" /tmp/sushi-project.out

for skill in \
  "$ROOT/skills/core/brainstorming/SKILL.md" \
  "$ROOT/skills/core/writing-plans/SKILL.md" \
  "$ROOT/skills/core/test-driven-development/SKILL.md" \
  "$ROOT/skills/core/systematic-debugging/SKILL.md" \
  "$ROOT/skills/core/requesting-code-review/SKILL.md" \
  "$ROOT/skills/core/verification-before-completion/SKILL.md"
do
  [[ -f "$skill" ]]
done

first="$("$ROOT/bin/ticket" "First task" "Do one thing")"
second="$("$ROOT/bin/ticket" "Second task" "Do another thing")"
[[ "$first" == "$TMP_STATE/projects/SUSH/tickets/SUSH-0001.md" ]]
[[ "$second" == "$TMP_STATE/projects/SUSH/tickets/SUSH-0002.md" ]]
grep -q '^Project: SUSH$' "$first"

"$ROOT/bin/project" create "OpenCode Migration" OPEN >/tmp/sushi-project2.out
third="$("$ROOT/bin/ticket" --project OPEN "Try OpenCode" "Switch engine")"
[[ "$third" == "$TMP_STATE/projects/OPEN/tickets/OPEN-0001.md" ]]

"$ROOT/bin/engines" list | grep -q opencode
"$ROOT/bin/engines" use opencode >/tmp/sushi-engine.out
grep -q "active engine: opencode" /tmp/sushi-engine.out
[[ "$("$ROOT/bin/engines" current)" == "opencode" ]]

"$ROOT/bin/status-board" append START SUSH-0001 $$ smoke
"$ROOT/bin/status-board" show 2 | grep -q SUSH-0001
mkdir -p "$TMP_STATE/projects/SUSH/logs"
printf 'smoke log\n' > "$TMP_STATE/projects/SUSH/logs/SUSH-0001.run.log"

"$ROOT/bin/doctor" | grep -q "doctor: PASS"
EXPORT_DIR="$(mktemp -d /tmp/sushi-export-test.XXXXXX)"
rm -rf "$EXPORT_DIR"
"$ROOT/bin/export-vanilla" "$EXPORT_DIR" | grep -q "Vanilla export ready"
"$ROOT/bin/share-doctor" "$EXPORT_DIR" | grep -q "share-doctor: PASS"

python3 -m py_compile "$ROOT/gui/server.py"
bash -n "$ROOT"/bin/*

PORT=$((18000 + $$ % 10000))
SUSHI_GUI_PORT="$PORT" python3 "$ROOT/gui/server.py" >/tmp/sushi-gui-test.out 2>&1 &
SERVER_PID=$!
for _ in {1..40}; do
  if curl -fs "http://127.0.0.1:$PORT/api/status" >/tmp/sushi-api-status.json 2>/dev/null; then
    break
  fi
  sleep 0.25
done

curl -fsS "http://127.0.0.1:$PORT/api/projects" | grep -q '"key": "SUSH"'
curl -fsS "http://127.0.0.1:$PORT/api/tickets?project=SUSH" | grep -q 'SUSH-0001'
curl -fsS "http://127.0.0.1:$PORT/api/doctor" | grep -q '"status": "pass"'
curl -fsS "http://127.0.0.1:$PORT/api/logs?project=SUSH" | grep -q 'SUSH-0001.run.log'

echo "smoke: PASS"
