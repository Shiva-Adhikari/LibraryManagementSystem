# third party modules
import jwt
import logging

# built in modules
import os

# local modules
from src.models import settings, db
from .http_server import _send_response, _input_access_token, _input_refresh_token


def logging_module():
    """logging module

    Returns:
        str: return logger configuration and path.
    """

    # Logging Module
    log_dir = os.path.abspath('logs')
    os.makedirs(log_dir, exist_ok=True)     # create dir if not exist
    log_path = os.path.join(log_dir, 'log_file.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)s %(funcName)s lineno: %(lineno)d '
        '%(levelname)s: %(message)s',
        filename=log_path,
        filemode='a'
    )

    return logging.getLogger(__name__)


# Instance
logger = logging_module()


@_send_response
def decode_token(self, token, SECRET_KEY, whoami):
    """Decode token to text

    Args:
        token (str): encoded token
        SECRET (str): secret key to decode

    Returns:
        str: return decoded token i.e user or admin credentials.
    """

    ALGORITHM = settings.JWT_ALGORITHM.get_secret_value()
    try:
        # this is used by professional, remember this for future
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=ALGORITHM,
            options={
                'require': ['iat', 'exp'],
                'verify_iat': ['iat'],
                'verify_exp': ['exp']
            })
        if decoded:
            return decoded

    except (
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        """if token is expired then it call refresh token to extend time.
        """
        from src import refresh_token
        print('\nexception')
        print('access token decode')
        auth_header = self.headers.get('Authorization')
        print('aa')
        if not auth_header:
            response = {'missing token': 'Missing or Invalid Access token'}
            return (response, 401)
        print('ab')
        if auth_header:
            if auth_header.startswith('Bearer '):
                input_access_token = auth_header.split(' ', 1)[1]
            else:
                input_access_token = auth_header  # Directly take the token
        print('ac')
        print('start aaa')
        if not input_access_token:
            return

        print('aaa decode token')
        if whoami == 'Admin':
            print('admin exec')
            SECRET = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()
        elif whoami == 'User':
            print('user exec')
            SECRET = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()
        print('bbb')
        token = refresh_token(input_access_token, SECRET)
        print(f'ccc: {token}')
        if token:
            print('got token')
            response = {
                'message': 'Refresh Token Key.',
                'token': token
            }
            return (response, 200)

    except Exception as e:
        logger.debug(e)
        response = {'exception': f'Token is invalid, Login Again.{str(e)}'}
        return (response, 400)


@_send_response
def _verify_refresh_token(self, whoami):
    token = self.headers.get('RefreshToken')
    if not token:
        response = {'missing token': 'Missing or Invalid Refresh token'}
        return (response, 401)
    print(f'refresh token: {token}')
    if not token:
        logger.error('token not found from header')
        return
    print('aa')
    if whoami == 'Admin':
        print('admin')
        SECRET_KEY = settings.ADMIN_SECRET_JWT.get_secret_value()
        token_data = decode_token(self, token, SECRET_KEY, whoami)
    elif whoami == 'User':
        print('user')
        SECRET_KEY = settings.USER_SECRET_JWT.get_secret_value()
        token_data = decode_token(self, token, SECRET_KEY, whoami)
    print('bb')
    if not token_data:
        return
    print('cc')
    return token_data


def find_keys():
    """check books available or not by searching Book Category

    Returns:
        str: return Books Category
    """

    categories = db.Books.find()
    keys = [next(iter(data.keys() - {'_id'})) for data in categories]
    if not keys:
        return False
    return keys


start_id = 0


def count_books(auto_id: int, category: str):
    """Get book id

    Args:
        auto_id (int): count list of books
        category (str): Book Name

    Returns:
        int: return Number of Books
    """

    global start_id
    try:
        count_book = db.Books.aggregate([
            {
                '$match': {category: {'$exists': True}}
            },
            {
                '$project': {
                    '_id': 0,
                    'count': {
                        '$add': [
                            {'$size': f'${category}'},
                            1
                        ]
                    }
                }
            }
        ]).next()['count']

        start_id = count_book + auto_id
        return start_id
    except StopIteration:
        start_id = auto_id + 1
        return start_id
