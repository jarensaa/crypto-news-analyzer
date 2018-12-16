import http.server
import socketserver
import os


def plot():
    PORT = 8000

    web_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.chdir(web_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print("Serving plot at port", PORT)
    httpd.serve_forever()
