# third party modules
import jwt
import logging

# built in modules
import os

# local modules
from src.models import settings, db
from .http_server import _send_response


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

        auth_header = self.headers.get('Authorization')
        if not auth_header:
            response = {'missing token': 'Missing or Invalid Access token'}
            return (response, 401)

        if auth_header:
            if auth_header.startswith('Bearer '):
                input_access_token = auth_header.split(' ', 1)[1]
            else:
                input_access_token = auth_header  # Directly take the token

        if not input_access_token:
            return

        if whoami == 'Admin':
            SECRET = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()
        elif whoami == 'User':
            SECRET = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

        token = refresh_token(self, input_access_token, SECRET)

        if token:
            response = {
                'message': 'Refresh Token Key.',
                'token': token
            }
            return response

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

    if not token:
        logger.error('token not found from header')
        return

    if whoami == 'Admin':
        SECRET_KEY = settings.ADMIN_SECRET_JWT.get_secret_value()
        token_data = decode_token(self, token, SECRET_KEY, whoami)
    elif whoami == 'User':
        SECRET_KEY = settings.USER_SECRET_JWT.get_secret_value()
        token_data = decode_token(self, token, SECRET_KEY, whoami)

    if not token_data:
        return

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
