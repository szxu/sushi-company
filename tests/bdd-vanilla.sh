#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="$(mktemp -d /tmp/sushi-vanilla-bdd.XXXXXX)"
cleanup() {
  rm -rf "$EXPORT_DIR"
}
trap cleanup EXIT

"$ROOT/bin/export-vanilla" "$EXPORT_DIR" >/tmp/sushi-vanilla-export.out
grep -q "Vanilla export ready" /tmp/sushi-vanilla-export.out

SUSHI_TEST_ROOT="$EXPORT_DIR" SUSHI_BDD_MODE=vanilla npm run bdd
