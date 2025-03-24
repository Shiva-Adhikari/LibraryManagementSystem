# local modules
from src import account_register, account_login
from src.models import settings


def user_register(handler):
    """This is where User Register.
    """

    whoami = 'User'
    account_register(handler, whoami)


def user_login(handler):
    """This is where User Login

    Returns:
        bool: if successfully login then it return True.
    """

    whoami = 'User'
    access_token = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

    success_login = account_login(handler, whoami, access_token)
    if success_login:
        return True
