import json


def _send_response(handler, data, status_code=200):
    handler.send_response(status_code)
    handler.send_header('Content-type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())


def _read_json(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return json.loads(post_data.decode('utf-8'))


def _input_access_token(handler):
    auth_header = handler.headers.get('Authorization')

    if auth_header:
        if auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ', 1)[1]
        else:
            access_token = auth_header  # Directly take the token

        return access_token
    else:
        response = {'missing token': 'Missing or Invalid Access token'}
        _send_response(handler, response, 401)
        return


def _input_refresh_token(handler):
    auth_refresh_token = handler.headers.get('RefreshToken')

    if auth_refresh_token:
        return auth_refresh_token
    else:
        response = {'missing token': 'Missing or Invalid Refresh token'}
        _send_response(handler, response, 401)
        return
