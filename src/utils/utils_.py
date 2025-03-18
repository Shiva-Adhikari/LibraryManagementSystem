# third party modules
import jwt
import logging
from tqdm import tqdm

# built in modules
import os
import json
import time

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


def remove_user_login_details():
    """remove user login file
    """

    # remove admin session
    path = data_path('user')
    if os.path.exists(path):
        os.remove(path)


def get_admin_login_details():
    """get admin login details from file

    Returns:
        str: return admin file details.
    """

    # save admin login session
    details = data_path('admin')
    if not os.path.exists(details):
        return False
    try:
        with open(details) as file:
            get_details = json.load(file)
            if get_details:
                return get_details
    except json.decoder.JSONDecodeError:
        return False


def remove_admin_login_details():
    """remove admin login file
    """

    path = data_path('admin')
    if os.path.exists(path):
        os.remove(path)


def remove_access_token():
    """Remove access token.
    """

    path = data_path('access_token')
    if os.path.exists(path):
        os.remove(path)


def logout():
    """Remove login details files.
    """

    remove_access_token()
    remove_admin_login_details()
    remove_user_login_details()


def decode_token(handler, token, SECRET):
    """Decode token to text

    Args:
        token (str): encoded token
        SECRET (str): secret key to decode

    Returns:
        str: return decoded token i.e user or admin credentials.
    """

    SECRET_KEY = SECRET
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
        return decoded
    except jwt.exceptions.ExpiredSignatureError:
        # if token is expired then it call refresh token to extend time.
        from src.account_manager import refresh_token

        admin = get_admin_login_details()
        user = get_user_login_details()
        if not (admin or user):
            logout()
            return

        if admin:
            access_token = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()
            token = refresh_token(handler, access_token)
        elif user:
            access_token = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()
            token = refresh_token(handler, access_token)

        if token:
            return token

    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        logout()
        response = {'token error': 'Your Token is invalid, Login Again.'}
        _send_response(handler, response, 400)
        return
    except Exception as e:
        logger.debug(e)
        logout()
        response = {'exception': f'Your Token is invalid, Login Again. {str(e)}'}
        _send_response(handler, response, 400)
        return


def verify_jwt_token(handler):
    """verify user token with file is available and valid or not

    Returns:
        str: if token is valid and successfully decoded then it return token.
    """

    admin = get_admin_login_details()
    user = get_user_login_details()

    if not (admin or user):
        logout()
        return

    try:
        if admin:
            SECRET = settings.ADMIN_SECRET_JWT.get_secret_value()
            token_data = decode_token(handler, admin, SECRET)

        elif user:
            SECRET = settings.USER_SECRET_JWT.get_secret_value()
            token_data = decode_token(handler, user, SECRET)

        if not token_data:
            return

        return token_data

    except Exception as e:
        logger.error(e)
        return


def tqdm_progressbar():
    """progress bar.
    """

    for _ in tqdm(range(0, 100), desc='Loading..'):
        time.sleep(0.01)


def get_access_token():
    """get access token

    Returns:
        str: get token from file and return it.
    """

    data_dir = data_path('access_token')
    if not os.path.exists(data_dir):
        logout()
        return

    try:
        with open(data_dir, 'r') as file:
            token = json.load(file)
            return token
    except FileNotFoundError:
        return


def token_blacklist(handler):
    """add token token to database to prevent, reuse of unused token.

    Returns:
        bool: token is already available and no need to set to blacklist.
    """

    from src.account_manager import dencode_access_token

    token = get_access_token()
    if not token:
        return

    admin = get_admin_login_details()
    user = get_user_login_details()
    if not (admin or user):
        return

    if admin:
        access_token = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()
    elif user:
        access_token = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

    data_json = dencode_access_token(handler, access_token)
    if not data_json:
        return

    id = data_json['id']
    account = data_json['account']

    account_exists = db.Accounts.find_one({f'{account}.id': id})
    if not account_exists:
        return False

    try:
        blacklist = db.Accounts.update_one(
            {f'{account}.id': id},
            {
                '$push': {
                    f'{account}.$.TokenBlacklist': {
                        'token': token
                    }
                }
            }
        )

        success = blacklist.modified_count > 0
        return success

    except Exception as e:
        logger.error(e)
        return


def validate_access_token():
    """check token is available or not in database

    Returns:
        bool: if token is available in dataase return true
                i.e we don't read again.
    """

    # account = ''
    admin = get_admin_login_details()
    user = get_user_login_details()
    if not (admin or user):
        logout()
        return

    if admin:
        account = 'Admin'
    elif user:
        account = 'User'

    token = get_access_token()
    if not token:
        return

    check_token = db.Accounts.aggregate([
        {'$unwind': f'${account}'},
        {'$unwind': f'${account}.TokenBlacklist'},
        {'$match': {f'{account}.TokenBlacklist.token': token}},
        {
            '$project': {
                'username': f'${account}.username',
                'token': f'${account}.TokenBlacklist.token'
            }
        }
    ])

    try:
        is_data = list(check_token)
        if is_data and is_data[0]:
            return True

    except IndexError as e:
        logger.error(e)
        return


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
