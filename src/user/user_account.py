# local modules
from src.account_manager import account_login
from src.account_manager import account_register
from src.models.settings import settings


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
    access_token = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

    success_login = account_login(whoami, access_token)
    if success_login:
        return True
