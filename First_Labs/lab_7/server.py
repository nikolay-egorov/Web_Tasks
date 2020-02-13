import http.server

def run(server_class=http.server.HTTPServer, handler_class=http.server.CGIHTTPRequestHandler):
    PORT = 8000
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print("Serving at port: ", PORT)
    httpd.serve_forever()


run()
