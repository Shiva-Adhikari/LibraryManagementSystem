import os
import json
import logging


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
    return details if os.path.exists(details) else False
    try:
        with open(details) as file:
            get_details = json.load(file)
            if get_details:
                return True
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
    return details if os.path.exists(details) else False
    try:
        with open(details) as file:
            get_details = json.load(file)
            if get_details:
                return True
    except json.decoder.JSONDecodeError:
        return False


def remove_admin_login_details():
    """remove admin session"""
    path = data_path('admin')
    if os.path.exists(path):
        os.remove(path)
