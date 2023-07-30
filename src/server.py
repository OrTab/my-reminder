from server.base_server import get_server, populate_request_handlers

host_name = "localhost"
port = 8080


def handle_get(req):
    req.send_response(200)
    req.send_header("Content-type", "text/html")
    req.end_headers()
    req.wfile.write(bytes("<html><head></head>", "utf-8"))
    req.wfile.write(
        bytes("<body><p>Request: {}</p></body></html>".format(req.path), "utf-8")
    )


def init_server():
    populate_request_handlers("GET", "/*", handle_get)


if __name__ == "__main__":
    init_server()
    server = get_server(port, host_name)
    print("server listening http://{}:{}".format(host_name, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
