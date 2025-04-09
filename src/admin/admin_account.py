# local modules
from src import account_register, account_login
from src.models import settings
from src.utils import route


@route('POST', '/api/admin/register')
def admin_register(self):
    """This is where admin register.
    """

    whoami = 'Admin'
    account_register(self, whoami)


@route('POST', '/api/admin/login')
def admin_login(self):
    """Admin login

    Returns:
        bool: return True.
    """

    whoami = 'Admin'
    access_token = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()

    success_login = account_login(self, whoami, access_token)
    if success_login:
        return True
