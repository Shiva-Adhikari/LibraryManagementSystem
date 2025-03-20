# built in modules
from http.server import BaseHTTPRequestHandler, HTTPServer

# local modules
from src.admin import (
    admin_register, admin_login,
    add_books, delete_books, update_books, search_books, stock_book
)
from src.user import (
    user_register, user_login,
    issue_books, return_books, list_books
)
from src.utils import _send_response
from src.models import mongo_config


class MainServer(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/admin/register':
            admin_register(self)
        elif self.path == '/api/admin/login':
            admin_login(self)
        elif self.path == '/api/user/register':
            user_register(self)
        elif self.path == '/api/user/login':
            user_login(self)
        elif self.path == '/api/admin/add-books':
            add_books(self)
        elif self.path == '/api/admin/search-books':
            search_books(self)
        elif self.path == '/api/admin/stock-books':
            stock_book(self)
        elif self.path == '/api/user/issue-books':
            issue_books(self)
        elif self.path == '/api/user/list-books':
            list_books(self)
        else:
            response = {'error': 'mistake is in path, /api/account/?'}
            _send_response(self, response, 404)

    def do_DELETE(self):
        if self.path == '/api/admin/delete-books':
            delete_books(self)
        else:
            response = {'error': 'mistake is in path, /api/account/?'}
            _send_response(self, response, 404)

    def do_PUT(self):
        if self.path == '/api/admin/update-books':
            update_books(self)
        elif self.path == '/api/user/return-books':
            return_books(self)
        else:
            response = {'error': 'mistake is in path, /api/account/?'}
            _send_response(self, response, 404)


class Server:
    def __init__(self):
        self.HOST = mongo_config.HOST
        self.PORT = 9999

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
