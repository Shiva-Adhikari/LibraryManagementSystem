# local modules
from src import account_register, account_login
from src.models import settings
from src.utils import route


@route('POST', '/api/user/register')
def user_register(self):
    """This is where User Register.
    """

    whoami = 'User'
    account_register(self, whoami)


@route('POST', '/api/user/login')
def user_login(self):
    """This is where User Login

    Returns:
        bool: if successfully login then it return True.
    """

    whoami = 'User'
    access_token = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

    success_login = account_login(self, whoami, access_token)
    if success_login:
        return True
