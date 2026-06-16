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

PORT = int(os.environ.get("SUSHI_GUI_PORT", "8444"))
WORKSPACE_DIR = os.environ.get(
    "COMPANY_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
SUSHI_HOME = os.environ.get("SUSHI_HOME", os.path.expanduser("~/.sushi"))
STATE_DIR = os.environ.get(
    "SUSHI_STATE_DIR",
    os.path.join(SUSHI_HOME, "company-state"),
)
TICKETS_DIR = os.path.join(STATE_DIR, "tickets")
PROJECTS_DIR = os.path.join(STATE_DIR, "projects")
LOGS_DIR = os.path.join(STATE_DIR, "logs")
STATUS_BOARD = os.path.join(STATE_DIR, "STATUS.md")
CURRENT_PROJECT_FILE = os.path.join(STATE_DIR, "current-project")

def current_project_key():
    env_key = os.environ.get("SUSHI_PROJECT_KEY", "").strip().upper()
    if re.match(r"^[A-Z]{4}$", env_key):
        return env_key
    if os.path.exists(CURRENT_PROJECT_FILE):
        with open(CURRENT_PROJECT_FILE, "r") as f:
            file_key = f.read().strip().upper()
        if re.match(r"^[A-Z]{4}$", file_key):
            return file_key
    return "SUSH"

def project_dirs(project_key=None):
    key = (project_key or current_project_key()).upper()
    project_dir = os.path.join(PROJECTS_DIR, key)
    return {
        "key": key,
        "project": project_dir,
        "tickets": os.path.join(project_dir, "tickets"),
        "work": os.path.join(project_dir, "work"),
        "logs": os.path.join(project_dir, "logs"),
    }

def parse_ticket_file(path, project_key):
    with open(path, 'r') as f:
        content = f.read()

    title_match = re.search(r'^#\s+([A-Z]{4}-\d{4})\s*(?::|--?|—)\s*(.*)$', content, re.M)
    status_match = re.search(r'^(?:\*\*)?Status(?:\*\*)?:\s*(.*)$', content, re.M)
    created_match = re.search(r'^(?:\*\*)?Created(?:\*\*)?:\s*(.*)$', content, re.M)
    if not title_match:
        return None
    return {
        "id": title_match.group(1),
        "title": title_match.group(2).strip(),
        "status": status_match.group(1).strip() if status_match else "UNKNOWN",
        "created": created_match.group(1).strip() if created_match else "UNKNOWN",
        "project": project_key,
        "filename": os.path.basename(path),
    }

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
            response = self.get_tickets(query.get("project", [None])[0])
        elif path == "/api/projects":
            response = self.get_projects()
        elif path == "/api/doctor":
            response = self.get_doctor()
        elif path == "/api/logs":
            response = self.get_logs(query)
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
        elif path == "/api/engines/use":
            response = self.use_engine(data)
        elif path == "/api/projects/use":
            response = self.use_project(data)
        elif path == "/api/projects/create":
            response = self.create_project(data)
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
            "state_dir": STATE_DIR,
            "current_project": current_project_key()
        }

    def get_tickets(self, project_key=None):
        query_key = (project_key or current_project_key()).upper()
        tickets_dir = project_dirs(query_key)["tickets"]
        tickets = []
        if os.path.exists(tickets_dir):
            for filename in sorted(os.listdir(tickets_dir)):
                if filename.endswith(".md"):
                    path = os.path.join(tickets_dir, filename)
                    ticket = parse_ticket_file(path, query_key)
                    if ticket:
                        tickets.append(ticket)
        return {"tickets": tickets}

    def get_projects(self):
        projects = []
        active = current_project_key()
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        for name in sorted(os.listdir(PROJECTS_DIR)):
            if not re.match(r"^[A-Z]{4}$", name):
                continue
            project_dir = os.path.join(PROJECTS_DIR, name)
            if not os.path.isdir(project_dir):
                continue
            display_name = f"{name} Project"
            meta = os.path.join(project_dir, "project.json")
            if os.path.exists(meta):
                try:
                    with open(meta, "r") as f:
                        display_name = json.load(f).get("name", display_name)
                except Exception:
                    pass
            ticket_data = self.get_tickets(name).get("tickets", [])
            open_count = len([t for t in ticket_data if t["status"] != "DONE"])
            done_count = len([t for t in ticket_data if t["status"] == "DONE"])
            projects.append({
                "key": name,
                "name": display_name,
                "active": name == active,
                "open": open_count,
                "done": done_count,
                "total": len(ticket_data),
            })
        return {"projects": projects, "current": active}

    def get_doctor(self):
        bin_doctor = os.path.join(WORKSPACE_DIR, "bin", "doctor")
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        env["SUSHI_HOME"] = SUSHI_HOME
        proc = subprocess.run([bin_doctor], capture_output=True, text=True, env=env)
        lines = [line for line in (proc.stdout + proc.stderr).splitlines() if line.strip()]
        return {
            "status": "pass" if proc.returncode == 0 else "fail",
            "returncode": proc.returncode,
            "lines": lines,
        }

    def get_logs(self, query):
        project_key = query.get("project", [current_project_key()])[0].upper()
        logs_dir = project_dirs(project_key)["logs"]
        logs = []
        if os.path.exists(logs_dir):
            for filename in sorted(os.listdir(logs_dir), reverse=True):
                if filename.endswith(".md") or filename.endswith(".run.log"):
                    path = os.path.join(logs_dir, filename)
                    stat = os.stat(path)
                    logs.append({
                        "ticket": filename.replace(".run.log", "").replace(".md", ""),
                        "filename": filename,
                        "project": project_key,
                        "modified": stat.st_mtime,
                        "size": stat.st_size,
                    })
        return {"logs": logs[:40]}

    def create_ticket(self, data):
        title = data.get("title", "Untitled Ticket")
        description = data.get("description", "")
        project_key = data.get("project", current_project_key()).upper()
        
        # Invoke ./bin/ticket
        bin_ticket = os.path.join(WORKSPACE_DIR, "bin", "ticket")
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        proc = subprocess.run([bin_ticket, "--project", project_key, title, description], capture_output=True, text=True, env=env)
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
        cfg_path = os.path.join(WORKSPACE_DIR, "config", "engines.json")
        with open(cfg_path, "r") as f:
            cfg = json.load(f)
        active_file = os.path.join(SUSHI_HOME, "active-engine")
        active = cfg.get("default", "copilot")
        if os.path.exists(active_file):
            with open(active_file, "r") as f:
                active = f.read().strip() or active
        states = {}
        for name, engine in cfg.get("engines", {}).items():
            home_dirs = engine.get("home_dirs", [])
            home_files = engine.get("home_files", [])
            tracked_home_paths = home_dirs + home_files
            primary = tracked_home_paths[0] if tracked_home_paths else f".{name}"
            path = os.path.expanduser(f"~/{primary}")
            is_linked = os.path.islink(path)
            resolves_to = os.readlink(path) if is_linked else ""
            existing_paths = [
                rel for rel in tracked_home_paths
                if os.path.exists(os.path.expanduser(f"~/{rel}")) or os.path.islink(os.path.expanduser(f"~/{rel}"))
            ]
            linked_paths = [
                rel for rel in home_dirs
                if os.path.islink(os.path.expanduser(f"~/{rel}")) and SUSHI_HOME in os.readlink(os.path.expanduser(f"~/{rel}"))
            ]
            command = engine.get("command", name)
            states[name] = {
                "label": engine.get("label", name),
                "command": command,
                "pitch": engine.get("pitch", ""),
                "exists": bool(existing_paths),
                "is_linked": bool(linked_paths),
                "resolves_to": resolves_to,
                "home_dirs": home_dirs,
                "home_files": home_files,
                "workspace_dirs": engine.get("workspace_dirs", []),
                "workspace_files": engine.get("workspace_files", []),
                "active": name == active
            }
        return {"engines": states, "active": active}

    def toggle_engine(self, data):
        engine = data.get("engine")
        if not engine:
            return {"status": "error", "message": "Missing engine"}
        if engine.startswith("."):
            engine = engine[1:]

        cfg_path = os.path.join(WORKSPACE_DIR, "config", "engines.json")
        with open(cfg_path, "r") as f:
            cfg = json.load(f)
        profile = cfg.get("engines", {}).get(engine)
        if not profile:
            return {"status": "error", "message": f"Unknown engine: {engine}"}
        
        home_dirs = profile.get("home_dirs", [f".{engine}"]) + profile.get("extra_config_dirs", [])
        timestamp = subprocess.run(["date", "+%s"], capture_output=True, text=True).stdout.strip()

        primary_path = os.path.expanduser(f"~/{home_dirs[0]}")
        if os.path.islink(primary_path):
            # Unlink
            for rel in home_dirs:
                path = os.path.expanduser(f"~/{rel}")
                if os.path.islink(path):
                    os.unlink(path)
            return {"status": "unlinked", "message": f"Successfully unlinked {engine} from ~/.sushi"}
        else:
            # Backup and Link
            for rel in home_dirs:
                path = os.path.expanduser(f"~/{rel}")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                if os.path.islink(path):
                    os.unlink(path)
                elif os.path.exists(path):
                    backup_path = f"{path}.backup-{timestamp}"
                    os.rename(path, backup_path)
                os.symlink(SUSHI_HOME, path)
            return {"status": "linked", "message": f"Successfully symlinked {engine} -> ~/.sushi"}

    def use_engine(self, data):
        engine = data.get("engine")
        if not engine:
            return {"status": "error", "message": "Missing engine"}
        bin_engines = os.path.join(WORKSPACE_DIR, "bin", "engines")
        env = os.environ.copy()
        env["SUSHI_HOME"] = SUSHI_HOME
        proc = subprocess.run([bin_engines, "use", engine], capture_output=True, text=True, env=env)
        if proc.returncode == 0:
            return {"status": "success", "message": proc.stdout.strip()}
        return {"status": "error", "message": proc.stderr or proc.stdout}

    def use_project(self, data):
        key = data.get("project", "").upper()
        if not re.match(r"^[A-Z]{4}$", key):
            return {"status": "error", "message": "Project key must be four uppercase letters"}
        bin_project = os.path.join(WORKSPACE_DIR, "bin", "project")
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        proc = subprocess.run([bin_project, "use", key], capture_output=True, text=True, env=env)
        if proc.returncode == 0:
            return {"status": "success", "message": proc.stdout.strip()}
        return {"status": "error", "message": proc.stderr or proc.stdout}

    def create_project(self, data):
        name = data.get("name", "")
        key = data.get("key", "")
        if not name:
            return {"status": "error", "message": "Missing project name"}
        bin_project = os.path.join(WORKSPACE_DIR, "bin", "project")
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        args = [bin_project, "create", name]
        if key:
            args.append(key.upper())
        proc = subprocess.run(args, capture_output=True, text=True, env=env)
        if proc.returncode == 0:
            return {"status": "success", "message": proc.stdout.strip()}
        return {"status": "error", "message": proc.stderr or proc.stdout}

    def trigger_ship(self, data):
        ticket_id = data.get("ticket_id")
        if not ticket_id:
            return {"status": "error", "message": "Missing ticket_id"}
        
        bin_ship = os.path.join(WORKSPACE_DIR, "bin", "ship")
        # Run in background via subprocess.Popen to prevent blocking the API
        project_key = ticket_id[:4] if re.match(r"^[A-Z]{4}-\d{4}$", ticket_id) else current_project_key()
        log_file = os.path.join(project_dirs(project_key)["logs"], f"{ticket_id}.run.log")
        
        # Ensure log folder exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"\n[GUI Triggered Ship for {ticket_id}]\n")
            
        # Popen runs completely asynchronously
        env = os.environ.copy()
        env["SUSHI_STATE_DIR"] = STATE_DIR
        env["SUSHI_PROJECT_KEY"] = project_key
        subprocess.Popen([bin_ship, ticket_id], stdout=open(log_file, "a"), stderr=subprocess.STDOUT, preexec_fn=os.setpgrp, env=env)
        return {"status": "success", "message": f"Launched shipping run for {ticket_id} in background."}

    def get_ship_output(self, ticket):
        if not ticket:
            return {"output": "No ticket selected."}
        
        project_key = ticket[:4] if re.match(r"^[A-Z]{4}-\d{4}$", ticket) else current_project_key()
        log_path = os.path.join(project_dirs(project_key)["logs"], f"{ticket}.run.log")
        if os.path.exists(log_path):
            with open(log_path, 'r', errors='replace') as f:
                lines = f.readlines()
            return {"output": "".join(lines[-150:])} # Return last 150 lines of logs
        return {"output": f"Waiting for logs to generate for {ticket}..."}

if __name__ == "__main__":
    # Ensure workspace directory matches current
    os.makedirs(os.path.join(WORKSPACE_DIR, "gui"), exist_ok=True)
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    dirs = project_dirs()
    os.makedirs(dirs["tickets"], exist_ok=True)
    os.makedirs(dirs["work"], exist_ok=True)
    os.makedirs(dirs["logs"], exist_ok=True)
    
    # zero-dependency local server; threaded so parallel browser API requests do not block each other.
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), SushiAPIHandler) as httpd:
        print(f"🍣 Sushi Company GUI API Server started at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down GUI Server.")
            httpd.server_close()
