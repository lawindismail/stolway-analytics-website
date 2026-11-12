#!/usr/bin/env python3
"""Preview the built site on your own computer with the same clean addresses the live server uses.

    python src/preview.py          then open http://localhost:8000

/about is answered by site/about.html, /about.html redirects to /about, and unknown addresses show the 404 page.
"""
import http.server, os, sys

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)

    def _redirect(self, to, query):
        self.send_response(301)
        self.send_header("Location", to + (("?" + query) if query else ""))
        self.end_headers()

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path.endswith("/index.html") or path.endswith("/index"):
            return self._redirect(path[: path.rindex("/") + 1], query)
        if path.endswith(".html") and path != "/404.html":
            return self._redirect(path[:-5], query)
        if len(path) > 1 and path.endswith("/"):
            return self._redirect(path.rstrip("/"), query)
        local = os.path.join(SITE, path.lstrip("/"))
        if path != "/" and os.path.isfile(local + ".html"):
            self.path = path + ".html" + (("?" + query) if query else "")
        elif path != "/" and not os.path.isfile(local):
            self.send_response(404)
            body = open(os.path.join(SITE, "404.html"), "rb").read()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    do_HEAD = do_GET


if __name__ == "__main__":
    print(f"Stolway site preview: http://localhost:{PORT}  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
