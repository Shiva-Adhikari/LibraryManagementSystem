# built in modules
import json
from urllib.parse import urlparse, parse_qs


def _send_response(function):
    def wrapper(self, *args, **kwargs):
        result = function(self, *args, **kwargs)
        data, status_code = result if isinstance(
            result, tuple) else (result, 200)

        if hasattr(self, 'send_response'):
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        return result
    return wrapper


def _read_json(function):
    def wrapper(self, *args, **kwargs):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            return function(self, body, *args, **kwargs)
        except Exception:
            response = {
                'status': 'error',
                'message': 'check your formatting before send request'
            }
            return (response, 400)
    return wrapper


def _read_get_query(function):
    def wrapper(self, *args, **kwargs):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        clean_data = {}
        for key, value in query_params.items():
            clean_data[key] = value[0]

        return function(self, clean_data, *args, **kwargs)
    return wrapper


ROUTES = {}


def route(method, path):
    def wrapper(function):
        ROUTES[(method, path)] = function
        return function
    return wrapper
