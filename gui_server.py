"""
gui_server.py
Lightweight local HTTP server for the BD26-EVENT Prospector Admin Board.
Zero third-party dependencies required.
"""

import http.server
import json
import os
import subprocess
import sys
import csv

PORT = 8080
CSV_FILE = "Egypt_Retail_Summit_2026_Prospects.csv"
CONFIG_FILE = "config.py"
PYTHON_EXE = sys.executable


class AdminRequestHandler(http.server.BaseHTTPRequestHandler):

    def _local_only(self) -> bool:
        """Reject requests not coming from the local browser."""
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin", "")
        return (
            host in ("localhost:8080", "127.0.0.1:8080")
            and origin in ("", f"http://{host}")
        )

    def log_message(self, format, *args):
        pass  # suppress noisy request logs

    def do_GET(self):
        if not self._local_only():
            self.send_error(403, "Forbidden")
            return
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("admin.html", "rb") as f:
                self.wfile.write(f.read())
            return

        elif self.path == "/api/config":
            import config
            data = {
                "HUNTER_API_KEY": getattr(config, "HUNTER_API_KEY", ""),
                "PROSPEO_API_KEY": getattr(config, "PROSPEO_API_KEY", ""),
                "SNOV_CLIENT_ID": getattr(config, "SNOV_CLIENT_ID", ""),
                "SNOV_CLIENT_SECRET": getattr(config, "SNOV_CLIENT_SECRET", ""),
                "APOLLO_API_KEY": getattr(config, "APOLLO_API_KEY", ""),
                "CREDIT_LIMIT": getattr(config, "CREDIT_LIMIT", 200),
                "PEOPLE_PER_DOMAIN": getattr(config, "PEOPLE_PER_DOMAIN", 5),
            }
            self.send_json(data)
            return

        elif self.path == "/api/prospects":
            prospects = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, mode="r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.reader(f)
                    try:
                        header = next(reader)
                    except StopIteration:
                        header = []
                    for row in reader:
                        if len(row) >= 7:
                            prospects.append({
                                "company": row[0],
                                "domain": row[1],
                                "source": row[2],
                                "name": row[3],
                                "title": row[4],
                                "email": row[5],
                                "linkedin": row[6],
                                "date": row[8] if len(row) > 8 else "",
                            })
            self.send_json(prospects)
            return

        elif self.path == "/api/download_csv":
            if os.path.exists(CSV_FILE):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{CSV_FILE}"')
                self.end_headers()
                with open(CSV_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "CSV file not found")
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        if not self._local_only():
            self.send_error(403, "Forbidden")
            return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body) if body else {}

        if self.path == "/api/config":
            self.update_config_file(payload)
            self.send_json({"status": "ok"})
            return

        elif self.path == "/api/scrape":
            provider = payload.get("provider", "hunter")
            output = payload.get("output", "csv")
            dry_run = payload.get("dry_run", False)

            cmd = [PYTHON_EXE, "scraper.py", "--provider", provider, "--output", output]
            if dry_run:
                cmd.append("--dry-run")

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=90,
                    encoding="utf-8",
                    errors="replace"
                )
                output_text = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
                self.send_json({"status": "ok", "output": output_text})
            except Exception as e:
                self.send_json({"status": "error", "output": f"Execution failed: {e}"})
            return

        self.send_error(404, "Endpoint not found")

    def update_config_file(self, data):
        # Update config.py with new keys and limits
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.startswith("HUNTER_API_KEY ="):
                new_lines.append(f'HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY", {json.dumps(str(data.get("HUNTER_API_KEY", "")))})\n')
            elif line.startswith("PROSPEO_API_KEY ="):
                new_lines.append(f'PROSPEO_API_KEY = os.environ.get("PROSPEO_API_KEY", {json.dumps(str(data.get("PROSPEO_API_KEY", "")))})\n')
            elif line.startswith("SNOV_CLIENT_ID ="):
                new_lines.append(f'SNOV_CLIENT_ID = os.environ.get("SNOV_CLIENT_ID", {json.dumps(str(data.get("SNOV_CLIENT_ID", "")))})\n')
            elif line.startswith("SNOV_CLIENT_SECRET ="):
                new_lines.append(f'SNOV_CLIENT_SECRET = os.environ.get("SNOV_CLIENT_SECRET", {json.dumps(str(data.get("SNOV_CLIENT_SECRET", "")))})\n')
            elif line.startswith("APOLLO_API_KEY ="):
                new_lines.append(f'APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", {json.dumps(str(data.get("APOLLO_API_KEY", "")))})\n')
            elif line.startswith("CREDIT_LIMIT ="):
                new_lines.append(f'CREDIT_LIMIT = {int(data.get("CREDIT_LIMIT", 200))}\n')
            elif line.startswith("PEOPLE_PER_DOMAIN ="):
                new_lines.append(f'PEOPLE_PER_DOMAIN = {int(data.get("PEOPLE_PER_DOMAIN", 5))}\n')
            else:
                new_lines.append(line)

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), AdminRequestHandler)
    print(f"BD26-EVENT Admin Board running at: http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Admin Board...")


if __name__ == "__main__":
    main()
