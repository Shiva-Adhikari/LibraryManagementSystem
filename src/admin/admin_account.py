# local modules
from src import account_register, account_login
from src.models import settings


def admin_register(handler):
    """This is where admin register.
    """

    whoami = 'Admin'
    account_register(handler, whoami)


def admin_login(handler):
    """Admin login

    Returns:
        bool: return True.
    """

    whoami = 'Admin'
    access_token = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()

    success_login = account_login(handler, whoami, access_token)
    if success_login:
        return True
