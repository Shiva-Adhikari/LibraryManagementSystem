# third party modules
import jwt
import click
import logging
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo import MongoClient

# built in modules
import os
import json
import time


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem

src_path = os.path.join('src')
env_path = os.path.join(src_path, '.env')
load_dotenv(env_path)


def data_path(file_name):
    """get file from directory

    Args:
        file_name (str): user or admin or access_token file

    Returns:
        str: return filename.
    """
    root_path = os.path.join(os.path.dirname(__file__))
    data_dir = os.path.join(root_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, f'{file_name}.json')
    return data_path


def logging_module():
    """logging module

    Returns:
        str: return logger configuration and path.
    """
    # Logging Module
    root_path = os.path.join(os.path.dirname(__file__))
    log_dir = os.path.join(root_path, 'logs')
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


def decode_token(token, SECRET):
    """Decode token to text

    Args:
        token (str): encoded token
        SECRET (str): secret key to decode

    Returns:
        str: return decoded token i.e user or admin credentials.
    """
    SECRET_KEY = os.getenv(SECRET)
    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256'],
            options={
                'require': ['iat', 'exp'],
                'verify_iat': ['iat'],
                'verify_exp': ['exp']
            })
        return decoded
    except jwt.exceptions.ExpiredSignatureError:
        # if token is expired then it call refresh token to extend time.
        from src.admin.admin_account import refresh_token

        admin = get_admin_login_details()
        user = get_user_login_details()
        token = ''

        if admin:
            access_token = 'ADMIN_SECRET_ACCESS_TOKEN'
            token = refresh_token(access_token)

        elif user:
            access_token = 'USER_SECRET_ACCESS_TOKEN'
            token = refresh_token(access_token)
        if token:
            return True

    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        logout()
        click.echo('Your Token is invalid, Login Again')
        time.sleep(1.1)
        return
    except Exception as e:
        logger = logging_module()
        logger.debug(e)
        logout()
        click.echo('Your Token is invalid, Login Again')
        return


def verify_jwt_token():
    """verify user token with file is available and valid or not

    Returns:
        str: if token is valid and successfully decoded then it return token.
    """
    admin = get_admin_login_details()
    user = get_user_login_details()

    try:
        if admin:
            SECRET = 'ADMIN_SECRET_JWT'
            token_data = decode_token(admin, SECRET)

        elif user:
            SECRET = 'USER_SECRET_JWT'
            token_data = decode_token(user, SECRET)

        else:
            return ''

        return token_data

    except Exception as e:
        logger = logging_module()
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
    try:
        with open(data_dir, 'r') as file:
            token = json.load(file)
            return token
    except FileNotFoundError:
        return


def token_blacklist():
    """add token token to database to prevent, reuse of unused token.

    Returns:
        bool: token is already available and no need to set to blacklist.
    """
    from src.admin.admin_account import dencode_access_token

    token = get_access_token()
    if not token:
        return

    admin = get_admin_login_details()
    user = get_user_login_details()
    if not (admin or user):
        return

    if admin:
        access_token = 'ADMIN_SECRET_ACCESS_TOKEN'
    elif user:
        access_token = 'USER_SECRET_ACCESS_TOKEN'

    data_json = dencode_access_token(access_token)
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
        logger = logging_module()
        logger.error(e)
        return


def validate_access_token():
    """check token is available or not in database

    Returns:
        bool: if token is available in dataase return true
                i.e we don't readd again.
    """
    account = ''
    admin = get_admin_login_details()
    user = get_user_login_details()
    if admin:
        account = 'Admin'
    elif user:
        account = 'User'
    else:
        logout()
        return

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
        logger = logging_module()
        logger.error(e)
        return
