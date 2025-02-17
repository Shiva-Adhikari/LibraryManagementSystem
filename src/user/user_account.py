import os
import jwt
import click
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

from config import logging_module
from src.admin.admin_account import account_login
from src.admin.admin_account import account_register


logger = logging_module()

src_path = os.path.join('src')
env_path = os.path.join(src_path, '.env')
load_dotenv(env_path)


def email_validation() -> str:
    while True:
        try:
            email = click.prompt('Enter Email', type=str)
            email = validate_email(email, check_deliverability=False)
            email = email.normalized
            return email
        except EmailNotValidError as e:
            click.echo(str(e))
            continue


def validate_token(extract_username_email):
    username = extract_username_email['username']
    email = extract_username_email['email']
    SECRET_KEY = os.getenv('jwt_user_secret')
    ALGORITHM = 'HS256'
    EXP_DATE = timedelta(minutes=5)
    payload = {
        'username': username,
        'email': email,
        'iat': int(datetime.now().timestamp()),
        'exp': int((datetime.now() + EXP_DATE).timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def user_register():
    whoami = 'User'
    account_register(whoami)


def user_login():
    whoami = 'User'
    access_token = 'SECRET_ACCESS_TOKEN_USER'
    # username = 'user'
    # password = 'user@123A'
    success_login = account_login(whoami, access_token)
    # success_login = account_login(whoami, access_token, username, password)
    if success_login:
        return True


if __name__ == '__main__':
    user_login()
