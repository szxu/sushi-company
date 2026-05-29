#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_STATE="$(mktemp -d /tmp/sushi-vanilla-test.XXXXXX)"
TMP_HOME="$(mktemp -d /tmp/sushi-home-test.XXXXXX)"
EXPORT_DIR=""
cleanup() {
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

"$ROOT/bin/doctor" | grep -q "doctor: PASS"
EXPORT_DIR="$(mktemp -d /tmp/sushi-export-test.XXXXXX)"
rm -rf "$EXPORT_DIR"
"$ROOT/bin/export-vanilla" "$EXPORT_DIR" | grep -q "Vanilla export ready"
"$ROOT/bin/share-doctor" "$EXPORT_DIR" | grep -q "share-doctor: PASS"

python3 -m py_compile "$ROOT/gui/server.py"
bash -n "$ROOT"/bin/*

echo "smoke: PASS"
