#!/usr/bin/env python3
# server.py — Zero-dependency HTTP API server for Sushi Company GUI Manager.
# Runs locally on port 8444. Compatible with MacOS Python 3.

import http.server
import socketserver
import json
import os
import re
import subprocess
from urllib.parse import urlparse, parse_qs

PORT = 8444
WORKSPACE_DIR = os.environ.get(
    "COMPANY_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
SUSHI_HOME = os.path.expanduser("~/.sushi")
STATE_DIR = os.environ.get(
    "SUSHI_STATE_DIR",
    os.path.join(SUSHI_HOME, "company-state"),
)
TICKETS_DIR = os.path.join(STATE_DIR, "tickets")
PROJECTS_DIR = os.path.join(STATE_DIR, "projects")
LOGS_DIR = os.path.join(STATE_DIR, "logs")
STATUS_BOARD = os.path.join(STATE_DIR, "STATUS.md")

class SushiAPIHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS for development/local browsing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.end_headers()

    def translate_path(self, path):
        # Explicitly map all static file paths to the gui/ subdirectory
        gui_dir = os.path.join(WORKSPACE_DIR, "gui")
        clean_path = urlparse(path).path.lstrip('/')
        if not clean_path:
            clean_path = "index.html"
        return os.path.join(gui_dir, clean_path)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        # Serve API routes
        if path.startswith("/api/"):
            self.handle_api_get(path, query)
        else:
            # Fallback to serving static HTML files natively via translate_path override
            super().do_GET()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path.startswith("/api/"):
            self.handle_api_post(path)
        else:
            self.send_error(404, "Not Found")

    # --- GET API Handlers ---
    def handle_api_get(self, path, query):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {"status": "ok"}

        if path == "/api/status":
            response = self.get_sushi_status()
        elif path == "/api/tickets":
            response = self.get_tickets()
        elif path == "/api/models":
            response = self.get_models()
        elif path == "/api/engines":
            response = self.get_engines()
        elif path == "/api/ship/output":
            ticket = query.get("ticket", [""])[0]
            response = self.get_ship_output(ticket)
        else:
            response = {"error": "Endpoint not found"}

        self.wfile.write(json.dumps(response).encode('utf-8'))

    # --- POST API Handlers ---
    def handle_api_post(self, path):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {"status": "ok"}

        if path == "/api/ticket":
            response = self.create_ticket(data)
        elif path == "/api/models/set":
            response = self.set_model_policy(data)
        elif path == "/api/engines/toggle":
            response = self.toggle_engine(data)
        elif path == "/api/ship":
            response = self.trigger_ship(data)
        else:
            response = {"error": "Endpoint not found"}

        self.wfile.write(json.dumps(response).encode('utf-8'))

    # --- Helper Logic Methods ---

    def get_sushi_status(self):
        board_path = STATUS_BOARD
        events = []
        if os.path.exists(board_path):
            with open(board_path, 'r') as f:
                lines = f.readlines()
            # Parse tab-separated events
            for line in lines:
                if re.match(r'^\d{4}-\d{2}-\d{2}', line):
                    parts = line.strip().split('\t')
                    if len(parts) >= 4:
                        events.append({
                            "timestamp": parts[0],
                            "event": parts[1],
                            "ticket": parts[2],
                            "pid": parts[3],
                            "note": parts[4] if len(parts) > 4 else ""
                        })
        
        # Check active processes
        active_processes = []
        try:
            pgrep = subprocess.run(["pgrep", "-af", "sushi-company/bin/(ship|sushi)"], capture_output=True, text=True)
            if pgrep.returncode == 0:
                for line in pgrep.stdout.strip().split('\n'):
                    if "status-board" not in line:
                        active_processes.append(line)
        except Exception:
            pass

        # Agents health check
        agents = []
        agents_dir = os.path.join(SUSHI_HOME, "agents")
        if os.path.exists(agents_dir):
            agents = [f.replace(".agent.md", "") for f in os.listdir(agents_dir) if f.endswith(".agent.md")]

        return {
            "events": events[-20:], # Return last 20 events
            "active_processes": active_processes,
            "agents": agents,
            "sushi_home": SUSHI_HOME,
            "workspace": WORKSPACE_DIR,
            "state_dir": STATE_DIR
        }

    def get_tickets(self):
        tickets_dir = TICKETS_DIR
        tickets = []
        if os.path.exists(tickets_dir):
            for filename in sorted(os.listdir(tickets_dir)):
                if filename.endswith(".md"):
                    path = os.path.join(tickets_dir, filename)
                    with open(path, 'r') as f:
                        content = f.read()
                    
                    # Extract title, status, and created date
                    title_match = re.search(r'^#\s+([A-Z]-[A-Z0-9-]+)\s*(?::|--?|—)\s*(.*)$', content, re.M)
                    status_match = re.search(r'^(?:\*\*)?Status(?:\*\*)?:\s*(.*)$', content, re.M)
                    created_match = re.search(r'^(?:\*\*)?Created(?:\*\*)?:\s*(.*)$', content, re.M)

                    if title_match:
                        tickets.append({
                            "id": title_match.group(1),
                            "title": title_match.group(2).strip(),
                            "status": status_match.group(1).strip() if status_match else "UNKNOWN",
                            "created": created_match.group(1).strip() if created_match else "UNKNOWN",
                            "filename": filename
                        })
        return {"tickets": tickets}

    def create_ticket(self, data):
        title = data.get("title", "Untitled Ticket")
        description = data.get("description", "")
        
        # Invoke ./bin/ticket
        bin_ticket = os.path.join(WORKSPACE_DIR, "bin", "ticket")
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        proc = subprocess.run([bin_ticket, title, description], capture_output=True, text=True, env=env)
        if proc.returncode == 0:
            ticket_file = proc.stdout.strip()
            ticket_id = os.path.basename(ticket_file).replace(".md", "")
            return {"status": "success", "ticket_id": ticket_id, "ticket_file": ticket_file}
        else:
            return {"status": "error", "message": proc.stderr}

    def get_models(self):
        cfg_path = os.path.join(WORKSPACE_DIR, "config", "models.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as f:
                return json.load(f)
        return {"error": "models.json not found"}

    def set_model_policy(self, data):
        role = data.get("role")
        model = data.get("model")
        if not role or not model:
            return {"status": "error", "message": "Missing role or model"}
        
        bin_models = os.path.join(WORKSPACE_DIR, "bin", "models")
        proc = subprocess.run([bin_models, "set", role, model], capture_output=True, text=True)
        if proc.returncode == 0:
            return {"status": "success", "message": proc.stdout.strip()}
        else:
            return {"status": "error", "message": proc.stderr}

    def get_engines(self):
        engines = [".copilot", ".gemini", ".agy", ".claude"]
        states = {}
        for eng in engines:
            path = os.path.expanduser(f"~/{eng}")
            is_linked = os.path.islink(path)
            resolves_to = os.readlink(path) if is_linked else ""
            states[eng] = {
                "exists": os.path.exists(path) or is_linked,
                "is_linked": is_linked and (SUSHI_HOME in resolves_to),
                "resolves_to": resolves_to
            }
        return {"engines": states}

    def toggle_engine(self, data):
        engine = data.get("engine") # e.g. ".copilot"
        if not engine.startswith("."):
            engine = f".{engine}"
        
        path = os.path.expanduser(f"~/{engine}")
        timestamp = subprocess.run(["date", "+%s"], capture_output=True, text=True).stdout.strip()

        if os.path.islink(path):
            # Unlink
            os.unlink(path)
            # Sync ~/.config/antigravity if .agy is unlinked
            if engine == ".agy":
                config_path = os.path.expanduser("~/.config/antigravity")
                if os.path.islink(config_path):
                    os.unlink(config_path)
            # Restore backup if available
            backup_pattern = os.path.expanduser(f"~/{engine}.backup-*")
            # Minimal fallback: just report unlinked
            return {"status": "unlinked", "message": f"Successfully unlinked {engine} from ~/.sushi"}
        else:
            # Backup and Link
            if os.path.exists(path):
                backup_path = f"{path}.backup-{timestamp}"
                os.rename(path, backup_path)
            os.symlink(SUSHI_HOME, path)
            # Sync ~/.config/antigravity if .agy is linked
            if engine == ".agy":
                config_path = os.path.expanduser("~/.config/antigravity")
                if os.path.islink(config_path):
                    os.unlink(config_path)
                elif os.path.exists(config_path):
                    os.rename(config_path, f"{config_path}.backup-{timestamp}")
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                os.symlink(SUSHI_HOME, config_path)
            return {"status": "linked", "message": f"Successfully symlinked {engine} -> ~/.sushi"}

    def trigger_ship(self, data):
        ticket_id = data.get("ticket_id")
        if not ticket_id:
            return {"status": "error", "message": "Missing ticket_id"}
        
        bin_ship = os.path.join(WORKSPACE_DIR, "bin", "ship")
        # Run in background via subprocess.Popen to prevent blocking the API
        log_file = os.path.join(LOGS_DIR, f"{ticket_id}.run.log")
        
        # Ensure log folder exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"\n[GUI Triggered Ship for {ticket_id}]\n")
            
        # Popen runs completely asynchronously
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        subprocess.Popen([bin_ship, ticket_id], stdout=open(log_file, "a"), stderr=subprocess.STDOUT, preexec_fn=os.setpgrp, env=env)
        return {"status": "success", "message": f"Launched shipping run for {ticket_id} in background."}

    def get_ship_output(self, ticket):
        if not ticket:
            return {"output": "No ticket selected."}
        
        log_path = os.path.join(LOGS_DIR, f"{ticket}.run.log")
        if os.path.exists(log_path):
            with open(log_path, 'r', errors='replace') as f:
                lines = f.readlines()
            return {"output": "".join(lines[-150:])} # Return last 150 lines of logs
        return {"output": f"Waiting for logs to generate for {ticket}..."}

if __name__ == "__main__":
    # Ensure workspace directory matches current
    os.makedirs(os.path.join(WORKSPACE_DIR, "gui"), exist_ok=True)
    os.makedirs(TICKETS_DIR, exist_ok=True)
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # zero-dependency TCPServer
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SushiAPIHandler) as httpd:
        print(f"🍣 Sushi Company GUI API Server started at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down GUI Server.")
            httpd.server_close()
