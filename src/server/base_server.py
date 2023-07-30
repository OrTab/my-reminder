from http.server import BaseHTTPRequestHandler, HTTPServer

requests_map = {}


def populate_request_handlers(method, path, handler):
    if method in requests_map:
        requests_map[method][path] = handler
    else:
        requests_map[method] = {path: handler}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        if self.command in requests_map:
            if self.path in requests_map[self.command]:
                requests_map[self.command][self.path](self)
                return

            if "/*" in requests_map[self.command]:
                requests_map[self.command]["/*"](self)

    def do_GET(self):
        self.handle_request()


def get_server(port, host_name):
    server_address = (host_name, port)
    return HTTPServer(server_address, MyHTTPRequestHandler)
