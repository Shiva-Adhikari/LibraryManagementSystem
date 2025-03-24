# third party modules
import jwt
import logging

# built in modules
import os
import json

# local modules
from src.models import settings, db
from src.utils.http_server import _send_response


def data_path(file_name):
    """get file from directory

    Args:
        file_name (str): user or admin or access_token file

    Returns:
        str: return filename.
    """

    data_dir = os.path.abspath('data')
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, f'{file_name}.json')
    return data_path


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
    logger = logging.getLogger(__name__)
    return logger


# Instance
logger = logging_module()


def get_user_login_details():
    """get user login details from file

    Returns:
        str: return user file details.
    """

    # save user login session
    details = data_path('user')
    if not os.path.exists(details):
        return False
    try:
        with open(details) as file:
            get_details = json.load(file)
            if get_details:
                return get_details
    except json.decoder.JSONDecodeError:
        return False


def decode_token(handler, token, SECRET_KEY, whoami):
    """Decode token to text

    Args:
        token (str): encoded token
        SECRET (str): secret key to decode

    Returns:
        str: return decoded token i.e user or admin credentials.
    """

    # SECRET_KEY = SECRET
    ALGORITHM = settings.JWT_ALGORITHM.get_secret_value()
    try:
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

        # # if token is expired then it call refresh token to extend time.
        from .http_server import _input_access_token
        from src.account_manager import refresh_token

        input_access_token = _input_access_token(handler)

        if not input_access_token:
            return

        # how to know user or admin secret key
        if whoami == 'Admin':
            SECRET = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()
        elif whoami == 'User':
            SECRET = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

        token = refresh_token(handler, input_access_token, SECRET)
        if token:
            response = {
                'message': 'Refresh Token Key.',
                'token': token
            }
            _send_response(handler, response, 200)

    except Exception as e:
        logger.debug(e)
        response = {'exception': f'Token is invalid, Login Again.{str(e)}'}
        _send_response(handler, response, 400)
        return


def _verify_refresh_token(handler, whoami):
    from .http_server import _input_refresh_token

    token = _input_refresh_token(handler)
    if not token:
        return

    if whoami == 'Admin':
        SECRET_KEY = settings.ADMIN_SECRET_JWT.get_secret_value()
        token_data = decode_token(handler, token, SECRET_KEY, whoami)

    elif whoami == 'User':
        SECRET_KEY = settings.USER_SECRET_JWT.get_secret_value()
        token_data = decode_token(handler, token, SECRET_KEY, whoami)

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


def validate_user(category, book_name, username):
    """check book is available or not in Database

    Args:
        category (str): Book Category
        book_name (str): user input Book Name
        username (str): user username

    Returns:
        bool: return True if Book is found.
    """

    check_user = db.Books.aggregate([
        {'$unwind': f'${category}'},
        {'$unwind': f'${category}.UserDetails'},
        {
            '$match': {
                f'{category}.UserDetails.Username': username,
                f'{category}.Title': book_name
            }
        }, {
            '$project': {
                '_id': 0,
                'username': f'${category}.UserDetails.Username'
            }
        }
    ])

    is_data = list(check_user)

    return bool(is_data)
