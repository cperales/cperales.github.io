import http.server
import socket
import threading
from pathlib import Path
import urllib.request

import pytest

@pytest.fixture(scope="module")
def http_server():
    root = Path(__file__).resolve().parents[1]
    handler = http.server.SimpleHTTPRequestHandler
    # In Python 3.7+, we can pass directory parameter to handler
    def create_handler(*args, **kwargs):
        return handler(*args, directory=str(root), **kwargs)

    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        host, port = sock.getsockname()

    httpd = http.server.ThreadingHTTPServer((host, port), create_handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()

    url = f"http://{host}:{port}"
    try:
        yield url
    finally:
        httpd.shutdown()
        thread.join()

def test_index_html(http_server):
    with urllib.request.urlopen(f"{http_server}/index.html") as response:
        assert response.status == 200
