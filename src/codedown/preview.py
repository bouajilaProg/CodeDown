"""Local browser workspace for Markdown preview; never writes the source file."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
from typing import Optional
from urllib.parse import unquote, urlsplit
import webbrowser

from codedown.converter import ConverterEngine, RenderOptions
from codedown.paths import ASSETS_DIR
from codedown.themes import get_all_themes, get_theme_by_name


def create_preview_server(source: Path, style: str = "dark",
                          options: Optional[RenderOptions] = None,
                          port: int = 0) -> ThreadingHTTPServer:
    source = source.resolve()
    get_theme_by_name(style)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, payload, content_type="application/json", status=200):
            data = json.dumps(payload).encode() if content_type == "application/json" else payload
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            route = urlsplit(self.path).path
            try:
                if route == "/":
                    config = json.dumps(dict(token=token, theme=style.lower(), filename=source.name,
                                             themes=[theme.name for theme in get_all_themes()]))
                    page = (ASSETS_DIR / "preview" / "index.html").read_text(encoding="utf-8")
                    page = page.replace("__CONFIG__", config.replace("<", "\\u003c"))
                    self.respond(page.encode(), "text/html; charset=utf-8")
                elif route == "/api/document":
                    self.respond(dict(markdown=source.read_text(encoding="utf-8")))
                elif route in {"/workspace.js", "/workspace.css"}:
                    asset = ASSETS_DIR / "preview" / route[1:]
                    mime = "text/javascript" if route.endswith(".js") else "text/css"
                    self.respond(asset.read_bytes(), mime + "; charset=utf-8")
                elif route.startswith("/assets/"):
                    asset = (source.parent / unquote(route[len("/assets/"):])).resolve()
                    if source.parent not in asset.parents or not asset.is_file():
                        self.respond(dict(error="Resource not found"), status=404)
                    else:
                        self.respond(asset.read_bytes(), mimetypes.guess_type(asset.name)[0] or "application/octet-stream")
                else:
                    self.respond(dict(error="Not found"), status=404)
            except (OSError, UnicodeError) as error:
                self.respond(dict(error=str(error)), status=400)

        def do_POST(self):
            if self.path != "/api/render":
                self.respond(dict(error="Not found"), status=404)
                return
            if self.headers.get("X-Preview-Token") != token:
                self.respond(dict(error="Invalid preview token"), status=403)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 5 * 1024 * 1024:
                    raise ValueError("Preview request must be between 1 byte and 5 MB")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or not isinstance(data.get("markdown"), str):
                    raise ValueError("markdown must be a string")
                theme = get_theme_by_name(data.get("theme", style))
                engine = ConverterEngine(data["markdown"], source, options)
                html = engine.apply_theme(engine.convert_to_html(), theme)
                html = html.replace("<head>", '<head><base href="/assets/">', 1)
                # Screen padding must override PDF layout settings only in the preview.
                html = html.replace("</head>", '<style>@media screen { body { padding: 24px; } }'
                                    '.copy-code { margin: 8px 0; } @media print { .copy-code { display: none; } }</style></head>', 1)
                self.respond(dict(html=html, css=theme.get_css()))
            except (ValueError, TypeError, AttributeError) as error:
                self.respond(dict(error=str(error)), status=400)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def run_preview(source: Path, style: str = "dark", options: Optional[RenderOptions] = None,
                port: int = 0, open_browser: bool = True):
    import typer
    with create_preview_server(source, style, options, port) as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        typer.echo(f"Preview: {url}\nPress Ctrl+C to stop. Browser edits do not change the source file.")
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
