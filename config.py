import os
import jwt
import json
import time
import click
import logging
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem

src_path = os.path.join('src')
env_path = os.path.join(src_path, '.env')
load_dotenv(env_path)


def data_path(file_name):
    """save login filepath"""
    root_path = os.path.join(os.path.dirname(__file__))
    data_dir = os.path.join(root_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, f'{file_name}.json')
    return data_path


def logging_module():
    """Logging Module"""
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
    """save user login session"""
    details = data_path('user')
    # return details if os.path.exists(details) else False
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
    """remove admin session"""
    path = data_path('user')
    if os.path.exists(path):
        os.remove(path)


def get_admin_login_details():
    """save admin login session"""
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
    """remove admin session"""
    path = data_path('admin')
    if os.path.exists(path):
        os.remove(path)


def remove_access_token():
    path = data_path('access_token')
    if os.path.exists(path):
        os.remove(path)


def logout():
    token = validate_access_token()
    if not token:
        token_blacklist()

    remove_access_token()
    remove_admin_login_details()
    remove_user_login_details()


def logmeout():
    remove_access_token()
    remove_admin_login_details()
    remove_user_login_details()


def decode_token(token, SECRET):
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
        from src.admin.admin_account import refresh_token

        admin = get_admin_login_details()
        user = get_user_login_details()
        token = ''

        if admin:
            access_token = 'SECRET_ACCESS_TOKEN_ADMIN'
            token = refresh_token(access_token)

        elif user:
            access_token = 'SECRET_ACCESS_TOKEN_USER'
            token = refresh_token(access_token)
        time.sleep(1.1)

        if token:
            return True

        return False
    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        logout()
        click.echo('Your Token is invalid, Login Again')
        time.sleep(1.1)
        return False
    except Exception as e:
        logger = logging_module()
        logger.debug(e)
        logout()
        return False


def verify_jwt_token():
    admin = get_admin_login_details()
    user = get_user_login_details()
    account = ''

    if admin:
        account = 'Admin'
        SECRET = 'jwt_admin_secret'
        token_data = decode_token(admin, SECRET)
        if not token_data:  # if token not found
            return False
    elif user:
        account = 'User'
        SECRET = 'jwt_user_secret'
        token_data = decode_token(user, SECRET)
        if not token_data:  # if token not found
            return False
    else:
        return '', ''
    return token_data, account


def tqdm_progressbar():
    for _ in tqdm(range(0, 100), desc='Loading..'):
        time.sleep(0.01)


def get_access_token():
    data_dir = data_path('access_token')
    try:
        with open(data_dir, 'r') as file:
            token = json.load(file)
            return token
    except FileNotFoundError:
        return


def token_blacklist():
    from src.admin.admin_account import dencode_access_token

    token = get_access_token()
    if not token:
        return

    verify, account = verify_jwt_token()
    if not verify:
        return

    data_json = ''

    if account == 'Admin':
        access_token = 'SECRET_ACCESS_TOKEN_ADMIN'
        data_json = dencode_access_token(access_token)
    elif account == 'User':
        access_token = 'SECRET_ACCESS_TOKEN_USER'
        data_json = dencode_access_token(access_token)

    id = data_json['id']
    account = data_json['account']

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

    if blacklist.modified_count > 0:
        return True
    else:
        return False


# check token is available or not in database
def validate_access_token():
    verify, account = verify_jwt_token()

    if not verify:
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
        return False
    except IndexError as e:
        logger = logging_module()
        logger.error(e)
        return False
