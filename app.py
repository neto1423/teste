from __future__ import annotations

import json
import ipaddress
import os
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, urlparse


ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / "downloads"
DOWNLOADS.mkdir(exist_ok=True)
JOBS: dict[str, dict] = {}
LOCK = threading.Lock()


def valid_video_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme not in {"https", "http"} or not host or parsed.username or parsed.password:
            return False
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            pass
        return True
    except ValueError:
        return False


def run_download(job_id: str, url: str) -> None:
    command = [
        sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-warnings",
        "--socket-timeout", "15", "--retries", "2", "--fragment-retries", "2",
        "--format", "best[ext=mp4]/best", "--restrict-filenames",
        "-o", str(DOWNLOADS / "%(title).100s-%(id)s.%(ext)s"),
        "--print", "after_move:filepath", url,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        output_path = next((Path(line.strip()) for line in reversed(result.stdout.splitlines()) if line.strip()), None)
        if result.returncode == 0 and output_path and output_path.is_file():
            with LOCK:
                JOBS[job_id].update(status="done", filename=output_path.name, error=None)
        else:
            message = result.stderr.strip().splitlines()
            explanation = message[-1] if message else "O Instagram não disponibilizou este vídeo."
            with LOCK:
                JOBS[job_id].update(status="error", error=explanation[:300])
    except subprocess.TimeoutExpired:
        with LOCK:
            JOBS[job_id].update(status="error", error="O download demorou demais. Tente novamente.")
    except Exception:
        with LOCK:
            JOBS[job_id].update(status="error", error="Não foi possível iniciar o download.")


class Handler(BaseHTTPRequestHandler):
    def send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/" or self.path == "/index.html":
            data = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path.startswith("/api/status/"):
            job_id = self.path.rsplit("/", 1)[-1]
            with LOCK:
                job = JOBS.get(job_id)
            if not job:
                self.send_json({"error": "Download não encontrado."}, 404)
            else:
                self.send_json(job)
            return
        if self.path.startswith("/api/file/"):
            name = self.path.rsplit("/", 1)[-1]
            path = DOWNLOADS / name
            if not path.is_file() or path.parent != DOWNLOADS:
                self.send_json({"error": "Arquivo não encontrado."}, 404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4" if path.suffix.lower() == ".mp4" else "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(path.name)}")
            self.send_header("Content-Length", str(path.stat().st_size))
            self.end_headers()
            with path.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    self.wfile.write(chunk)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/download":
            self.send_error(404)
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 10_000)
            body = json.loads(self.rfile.read(length))
            url = str(body.get("url", "")).strip()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Envie um link válido."}, 400)
            return
        if not valid_video_url(url):
            self.send_json({"error": "Cole um link HTTP ou HTTPS válido de vídeo."}, 400)
            return
        job_id = uuid.uuid4().hex
        with LOCK:
            JOBS[job_id] = {"status": "downloading"}
        threading.Thread(target=run_download, args=(job_id, url), daemon=True).start()
        self.send_json({"id": job_id}, 202)

    def log_message(self, format: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Instagram Video Downloader em http://{host}:{port}")
    print("Pressione Ctrl+C para encerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()
