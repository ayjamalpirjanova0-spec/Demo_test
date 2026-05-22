"""
Replit uchun keep-alive server.
UptimeRobot bilan birga ishlatiladi.
"""
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, *args):  # silence access logs
        pass


def keep_alive():
    server = HTTPServer(("0.0.0.0", 8080), _Handler)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    print("✅ Keep-alive server :8080 da ishlamoqda")
