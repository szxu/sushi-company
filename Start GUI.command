#!/usr/bin/env bash
# Start GUI — Click-n-go launcher for Sushi Company macOS GUI.
# Double-click this file in macOS Finder to launch the dashboard.

set -euo pipefail

# Find absolute directory where this command script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# ANSI color codes
BOLD="\033[1m"
PURPLE="\033[38;2;191;148;255m"
CYAN="\033[38;2;135;206;250m"
RESET="\033[0m"

echo -e "${BOLD}${PURPLE}🍣 Starting Sushi Company GUI Dashboard...${RESET}"

# Kill any existing server on port 8444
if lsof -ti:8444 >/dev/null 2>&1; then
  echo "  Stopping existing GUI server on port 8444..."
  lsof -ti:8444 | xargs kill -9 || true
fi

# Run the zero-dependency Python API server
python3 gui/server.py &
SERVER_PID=$!

# Register exit trap to clean up server on window close
_cleanup() {
  echo -e "\n${BOLD}${CYAN}  Stopping GUI Server (PID: $SERVER_PID)...${RESET}"
  kill "$SERVER_PID" 2>/dev/null || true
}
trap _cleanup EXIT

# Wait a brief moment for the socket to bind
sleep 1.5

echo -e "${BOLD}${CYAN}🎨 Opening macOS Glassmorphism Dashboard...${RESET}"
open "http://localhost:8444/index.html"

echo -e "\n🟢 GUI Server is actively running."
echo -e "   Keep this Terminal window open while using the dashboard."
echo -e "   Press ${BOLD}Ctrl+C${RESET} in this window to stop the server."

# Keep terminal active and wait for the background server process
wait "$SERVER_PID"
