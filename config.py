import os
import jwt
import json
import time
import click
import logging
from dotenv import load_dotenv


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


def decode_token(token):
    SECRET_KEY = os.getenv('jwt_password')
    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256'],
            options={
                'require': ['iat', 'exp'],
                'verify_iss': ['iat'],
                'verify_exp': ['exp']
            })
        return decoded
    except jwt.exceptions.InvalidTokenError and jwt.DecodeError:
        remove_admin_login_details()
        remove_user_login_details()
        click.echo('Your Token is invalid, Login Again')
        return
    except Exception as e:
        logger = logging_module()
        logger.debug(e)
        return
    finally:
        time.sleep(2)


def verify_jwt_token():
    admin = get_admin_login_details()
    user = get_user_login_details()

    if admin:
        token_data = decode_token(admin)
    elif user:
        token_data = decode_token(user)
    else:
        return
    return token_data


if __name__ == '__main__':
    verify_jwt_token()
