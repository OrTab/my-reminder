import sys
import os

parent_dir = os.path.abspath("..")
sys.path.append(parent_dir)
from urllib.parse import parse_qs
from server.base_server import get_server, populate_request_handlers

host_name = "localhost"
port = 8080

cached_events = None


def handle_get(req):
    req.send_response(200)
    req.send_header("Content-type", "text/html")
    req.end_headers()
    req.wfile.write(bytes("<html><head></head>", "utf-8"))
    req.wfile.write(
        bytes("<body><p>Request: {}</p></body></html>".format(req.path), "utf-8")
    )


def handle_post(req):
    content_length = int(req.headers["Content-Length"])
    data = req.rfile.read(content_length)
    call_data = parse_qs(data.decode("utf-8"))
    call_id = call_data["CallSid"][0]
    call_status = call_data["CallStatus"][0]
    target_event = None
    for event in cached_events["data"]:
        if event["call_id"] == call_id:
            target_event = event
            break

    if target_event != None:
        print(call_status)


def init_server(events):
    global cached_events
    cached_events = events
    populate_request_handlers("POST", "/call", handle_post)
    server = get_server(port, host_name)
    print("server listening http://{}:{}".format(host_name, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
