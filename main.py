from http.server import BaseHTTPRequestHandler, HTTPServer
from src.admin import admin_register
from src.utils import _send_response
# import json


class MainServer(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/admin/register':
            admin_register(self)
        elif self.path == '/api/admin/login':
            # from src.admin import admin_login
            # admin_login()
            pass
        elif self.path == '/api/user/register':
            # self._account_register()
            pass
        elif self.path == '/api/user/login':
            # self._account_login()
            pass
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
