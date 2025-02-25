# third party modules
from dotenv import load_dotenv

# built in modules
import os

# local modules
from utils import logging_module
from src.admin.admin_account import account_login
from src.admin.admin_account import account_register


logger = logging_module()

src_path = os.path.join('src')
env_path = os.path.join(src_path, '.env')
load_dotenv(env_path)


def user_register():
    """This is where User Register.
    """
    whoami = 'User'
    account_register(whoami)


def user_login():
    """This is where User Login

    Returns:
        bool: if successfully login then it return True.
    """
    whoami = 'User'
    access_token = 'SECRET_ACCESS_TOKEN_USER'
    success_login = account_login(whoami, access_token)
    if success_login:
        return True
