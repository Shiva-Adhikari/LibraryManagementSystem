# local modules
from src.account_manager import account_register
from src.account_manager import account_login
from src.models.settings import settings


def admin_register():
    """This is where admin register.
    """
    whoami = 'Admin'
    account_register(whoami)


def admin_login():
    """Admin login

    Returns:
        bool: return True.
    """
    whoami = 'Admin'
    access_token = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()

    success_login = account_login(whoami, access_token)
    if success_login:
        return True
