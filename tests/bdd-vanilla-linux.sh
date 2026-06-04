#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_PARENT="${SUSHI_TEST_TMPDIR:-$HOME/.sushi/tmp}"
mkdir -p "$TMP_PARENT"
EXPORT_DIR="$(mktemp -d "$TMP_PARENT/sushi-vanilla-linux.XXXXXX")"
cleanup() {
  rm -rf "$EXPORT_DIR"
}
trap cleanup EXIT

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for the clean Linux vanilla BDD gate." >&2
  exit 2
fi

"$ROOT/bin/export-vanilla" "$EXPORT_DIR" >/tmp/sushi-vanilla-linux-export.out
grep -q "Vanilla export ready" /tmp/sushi-vanilla-linux-export.out

docker run --rm \
  -v "$EXPORT_DIR:/workspace/sushi-company" \
  -w /workspace/sushi-company \
  mcr.microsoft.com/playwright:v1.56.1-noble \
  /bin/bash -lc 'npm ci && SUSHI_TEST_ROOT=/workspace/sushi-company SUSHI_BDD_MODE=vanilla npm run bdd'
