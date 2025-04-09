# built in modules
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# local modules
from src.admin import (  # noqa: F401
    admin_register, admin_login,
    add_books, delete_books, update_books, search_books, stock_book
)
from src.user import (  # noqa: F401
    user_register, user_login,
    issue_books, return_books, list_books, user_issue_books_list
)
from src.utils import _send_response, ROUTES
from src.models import mongo_config, http_server


class MainServer(BaseHTTPRequestHandler):
    @_send_response
    def request_me(self):
        parsed_url = urlparse(self.path).path
        key = (self.command, parsed_url)

        handler = ROUTES.get(key)
        if handler:
            return handler(self)
        else:
            response = {'error': 'mistake is in path, /api/account/?'}
            return (response, 401)

    def do_GET(self):
        self.request_me()

    def do_POST(self):
        self.request_me()

    def do_PUT(self):
        self.request_me()

    def do_DELETE(self):
        self.request_me()


class Server:
    def __init__(self):
        self.HOST = mongo_config.HOST
        self.PORT = http_server.HTTPSERVER_PORT

    def __enter__(self):
        self.server = HTTPServer((self.HOST, self.PORT), MainServer)
        print("Server is Running...")
        return self.server

    def __exit__(self, exc_type, exc_value, traceback):
        if self.server:
            self.server.server_close()
            print('Server Stopped.')


if __name__ == '__main__':
    with Server() as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('server interrupted by user.')
