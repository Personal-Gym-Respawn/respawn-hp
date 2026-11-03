"""Loopback-only QA server. Serves the built package, never the repository root."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from build_oauth import OUTPUT


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path == '/__qa__/':
            # Local-only responsive harness: each iframe has its own real layout viewport.
            # No injected JavaScript and no changes to the public pages or build output.
            html = ('<!doctype html><html lang="en"><title>Local responsive QA</title>'
                    '<body><h1>Local responsive QA</h1>')
            for width in (320, 390, 768):
                for route, name in (('/', 'home'), ('/gbp-automation/', 'app'), ('/privacy/', 'privacy'), ('/404.html', 'error')):
                    html += (f'<h2>{name} {width}px</h2><iframe title="{name}-{width}" '
                             f'src="{route}" width="{width}" height="844"></iframe>')
            body = (html + '</body></html>').encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if urlsplit(self.path).path in ('/_headers', '/robots.txt'):
            # _headers is platform configuration, not a downloadable document on Pages.
            if urlsplit(self.path).path == '/_headers':
                self.send_error(404)
                return
        super().do_GET()

    def end_headers(self):
        # Emulate relevant Pages headers for local QA. The iframe harness deliberately
        # omits frame restrictions so it can test layout without changing public assets.
        if urlsplit(self.path).path != '/__qa__/':
            for line in (OUTPUT/'_headers').read_text().splitlines():
                if line.startswith('  ') and ':' in line:
                    key, value = line.strip().split(':', 1)
                    if key not in {'X-Frame-Options', 'Content-Security-Policy'}:
                        self.send_header(key, value.strip())
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'none'")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404)
        return None

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            body = (OUTPUT/'404.html').read_bytes()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)
            return
        super().send_error(code, message, explain)


if __name__ == '__main__':
    print('Local QA only: http://127.0.0.1:8764/ (responsive harness: /__qa__/)', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8764), Handler).serve_forever()
