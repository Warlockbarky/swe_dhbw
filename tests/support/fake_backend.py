import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import parse_qs, urlparse


class FakeBackendServer:
    def __init__(self, files=None, username="user", password="pass", token="token"):
        self.username = username
        self.password = password
        self.token = token
        self.files = files or [
            {
                "id": 1,
                "name": "report.pdf",
                "size": 123,
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "id": 2,
                "name": "notes.txt",
                "size": 456,
                "created_at": "2024-01-02T00:00:00",
            },
        ]
        self.file_bytes = {
            "1": b"PDF-DATA",
            "2": b"Notes",
        }
        self.httpd = None
        self.thread = None
        self.port = None

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.port}"

    def start(self):
        handler = self._build_handler()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.httpd.server_address[1]
        self.thread = Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread is not None:
            self.thread.join(timeout=2)

    def _build_handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return

            def _send_json(self, status, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _send_bytes(self, status, data, content_type="application/octet-stream"):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _is_authorized(self):
                header = self.headers.get("Authorization", "")
                return header == f"Bearer {server.token}"

            def do_POST(self):
                parsed = urlparse(self.path)
                if parsed.path == "/token":
                    length = int(self.headers.get("Content-Length", "0"))
                    body = self.rfile.read(length).decode("utf-8")
                    data = parse_qs(body)
                    username = (data.get("username") or [""])[0]
                    password = (data.get("password") or [""])[0]
                    if username == server.username and password == server.password:
                        self._send_json(200, {"access_token": server.token})
                    else:
                        self._send_json(401, {"detail": "invalid"})
                    return
                if parsed.path == "/register":
                    length = int(self.headers.get("Content-Length", "0"))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        self._send_json(400, {"detail": "bad json"})
                        return
                    if data.get("username") == "existing":
                        self._send_json(400, {"detail": "exists"})
                        return
                    self._send_json(201, {"status": "created"})
                    return
                if parsed.path == "/files/upload":
                    if not self._is_authorized():
                        self._send_json(401, {"detail": "unauthorized"})
                        return
                    self._send_json(201, {"status": "uploaded"})
                    return
                self._send_json(404, {"detail": "not found"})

            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/files/":
                    if not self._is_authorized():
                        self._send_json(401, {"detail": "unauthorized"})
                        return
                    self._send_json(200, list(server.files))
                    return
                if parsed.path.startswith("/files/") and parsed.path.endswith("/download"):
                    if not self._is_authorized():
                        self._send_json(401, {"detail": "unauthorized"})
                        return
                    parts = parsed.path.strip("/").split("/")
                    file_id = parts[1] if len(parts) > 2 else ""
                    data = server.file_bytes.get(file_id)
                    if data is None:
                        self._send_json(404, {"detail": "not found"})
                        return
                    self._send_bytes(200, data, content_type="application/octet-stream")
                    return
                self._send_json(404, {"detail": "not found"})

            def do_DELETE(self):
                parsed = urlparse(self.path)
                if parsed.path.startswith("/files/"):
                    if not self._is_authorized():
                        self._send_json(401, {"detail": "unauthorized"})
                        return
                    parts = parsed.path.strip("/").split("/")
                    file_id = parts[1] if len(parts) > 1 else ""
                    if file_id in server.file_bytes:
                        server.file_bytes.pop(file_id, None)
                        server.files = [f for f in server.files if str(f.get("id")) != file_id]
                        self.send_response(204)
                        self.end_headers()
                        return
                    self._send_json(404, {"detail": "not found"})
                    return
                self._send_json(404, {"detail": "not found"})

        return Handler
