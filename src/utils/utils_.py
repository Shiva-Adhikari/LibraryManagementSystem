# third party modules
import jwt
import logging

# built in modules
import os

# local modules
from src.models import db
from src.utils.http_server import _send_response
from src.utils.enums import Env


def logging_module():
    """logging module

    Returns:
        str: return logger configuration and path.
    """

    # Logging Module
    log_dir = os.path.abspath('logs')
    os.makedirs(log_dir, exist_ok=True)     # create dir if not exist
    log_path = os.path.join(log_dir, 'log_file.log')

    console_format = '%(message)s'
    file_format = (
        '%(asctime)s %(filename)s %(funcName)s lineno: %(lineno)d '
        '%(levelname)s: %(message)s'
    )

    class InfoOnlyFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.INFO

    class ExcludeInfoFilter(logging.Filter):
        def filter(self, record):
            return record.levelno != logging.INFO

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(log_path)

        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)

        console_handler.addFilter(InfoOnlyFilter())
        file_handler.addFilter(ExcludeInfoFilter())

        console_formatter = logging.Formatter(console_format)
        file_formatter = logging.Formatter(file_format)

        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


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

    ALGORITHM = Env.JWT_ALGORITHM.value
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
            SECRET = Env.ADMIN_SECRET_ACCESS_TOKEN.value
        elif whoami == 'User':
            SECRET = Env.USER_SECRET_ACCESS_TOKEN.value

        token = refresh_token(self, input_access_token, SECRET)

        if token:
            response = {
                'message': 'Refresh Token Key. Save it',
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

    if whoami == 'Admin':
        SECRET_KEY = Env.ADMIN_SECRET_JWT.value
        token_data = decode_token(self, token, SECRET_KEY, whoami)
    elif whoami == 'User':
        SECRET_KEY = Env.USER_SECRET_JWT.value
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
