# built in modules
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote
import re

# local modules
from src.admin import (  # noqa: F401
    admin_register, admin_login,
    add_books, delete_books, update_books, search_books, stock_book
)
from src.user import (  # noqa: F401
    user_register, user_login,
    issue_books, return_books, list_books, user_issue_books_list
)
from src.utils import (
    _send_response,
    ROUTES, logger, Env
)


class MainServer(BaseHTTPRequestHandler):
    @_send_response
    def request_me(self):
        re_path = urlparse(self.path).path

        try:
            key = (self.command, re_path)
            handler = ROUTES.get(key)
            if handler:
                return handler(self)

            for (method, pattern), func in ROUTES.items():
                if method == self.command:
                    match = re.match(pattern, re_path)
                    if match:
                        raw_category = match.group('category')
                        decoded_category = unquote(raw_category)
                        self.Category = decoded_category.strip().lower()
                        return func(self)

            raise TypeError('"mistake is in path, /api/account/?"')
        except Exception:
            response = {
                'status': 'error',
                'message': 'mistake is in path, /api/account/?'
            }
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
        self.HOST = Env.HOST.value
        self.PORT = Env.HTTPSERVER_PORT.value

    def __enter__(self):
        self.server = HTTPServer((self.HOST, self.PORT), MainServer)
        logger.info('Server is Running...')
        return self.server

    def __exit__(self, exc_type, exc_value, traceback):
        if self.server:
            self.server.server_close()
            logger.info('Server Stopped.')


if __name__ == '__main__':
    with Server() as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info('server interrupted by user.')
