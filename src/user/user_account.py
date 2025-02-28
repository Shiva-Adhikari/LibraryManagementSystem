# local modules
from src.admin.admin_account import account_login
from src.admin.admin_account import account_register


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
    access_token = 'USER_SECRET_ACCESS_TOKEN'
    success_login = account_login(whoami, access_token)
    if success_login:
        return True
