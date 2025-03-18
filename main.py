from http.server import BaseHTTPRequestHandler, HTTPServer
from src.admin import (
    admin_register, admin_login,
    add_books, delete_books, update_books, search_books, stock_book
)
from src.utils import _send_response
from src.user import (
    user_register, user_login,
    issue_books
)


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
        else:
            response = {'error': 'mistake is in path, /api/account/?'}
            _send_response(self, response, 404)


if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 9999
    server = HTTPServer((HOST, PORT), MainServer)
    print("Server is Running...")
    server.serve_forever()
    server.server_close()
    print('Server Stopped.')
