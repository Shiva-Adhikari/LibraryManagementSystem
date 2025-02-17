# this no need to install
import os
import json
from datetime import datetime, timedelta  # combine is better

# this need to install
import jwt
import click
import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient
from password_validator import PasswordValidator
from email_validator import validate_email, EmailNotValidError

from config import logout
# from config import logmeout

# import from file
from config import data_path
from config import logging_module


logger = logging_module()

src_path = os.path.join('src')
env_path = os.path.join(src_path, '.env')
load_dotenv(env_path)

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


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


def password_validation(password: str):
    """password validation"""
    # creating PasswordValidator object
    validator = PasswordValidator()
    # Define the password rules
    validator.min(8)             # minimum length
    validator.max(20)            # maximum length
    validator.has().uppercase()  # must have at least one uppercase letter
    validator.has().lowercase()  # must have at least one lowercase letter
    validator.has().digits()     # must have at least one digit
    validator.has().symbols()    # must have at least one special character
    validator.no().spaces()      # no spaces allowed
    try:
        # check password is valid or not
        if validator.validate(password):
            return password
        else:
            click.echo(
                'Password must be 8+ characters with upper, lower, '
                'digit, and special symbols.'
            )
    except Exception as e:
        click.echo(f'Password not valid: {str(e)}')
        return None


def confirm_password_validation() -> str:
    """get password and return"""
    while True:
        while True:
            password = click.prompt('Enter password', type=str)
            password = password_validation(password)
            if password:
                break
        while True:
            confirm_password = click.prompt('Enter confirm password', type=str)
            confirm_password = password_validation(confirm_password)
            if confirm_password:
                break
        if password == confirm_password:
            # create salt
            salt = bcrypt.gensalt(rounds=10)
            # convert password to hash with added salt
            password = bcrypt.hashpw(password.encode(), salt)
            return password
        else:
            click.echo('password not match')


def check_accounts(account, username):
    fetch_account = db.Accounts.aggregate([
        {'$unwind': f'${account}'},
        {'$match': {f'{account}.username': username}},
        {'$project': {'username': f'${account}.username', '_id': 0}}
    ])
    check_account = list(fetch_account)
    if check_account:
        return True
    else:
        return False


def validation(admin) -> tuple[str, str]:
    """get username and return with password"""
    while True:
        username = click.prompt('Enter Username', type=str).lower().strip()
        if len(username) > 3:
            account = check_accounts(admin, username)
            if account:
                click.echo("Username exits check another\n")
                continue
            break
        click.echo('username must be more than 4 letter long\n')
    password = confirm_password_validation()
    return username, password


def admin_register():
    whoami = 'Admin'
    account_register(whoami)


def account_register(whoami):
    """save in database"""
    try:
        username, password = validation(whoami)
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        id = _count_accounts(whoami)
        add_accounts = {}

        if whoami == 'Admin':
            add_accounts = db.Accounts.update_one(
                {f'{whoami}': {'$exists': True}},
                {'$push': {
                    f'{whoami}': {
                        'id': id,
                        'username': username,
                        'password': password
                    }
                }},
                upsert=True
            )
        elif whoami == 'User':
            email = email_validation()
            if not email:
                return

            add_accounts = db.Accounts.update_one(
                {f'{whoami}': {'$exists': True}},
                {'$push': {
                    f'{whoami}': {
                        'id': id,
                        'username': username,
                        'email': email,
                        'password': password
                    }
                }},
                upsert=True
            )

        if add_accounts.modified_count > 0 or add_accounts.upserted_id:
            click.echo('Register Successfully')
        else:
            logger.error('Register Failed')
            click.echo('Register Failed')
            return
    except Exception as e:
        logger.error(e)
        click.echo(f'Got Exception in register: {e}')
        return


def admin_login():
    whoami = 'Admin'
    access_token = 'SECRET_ACCESS_TOKEN_ADMIN'

    # username = 'admin'
    # password = 'admin@123A'
    # success_login = account_login(whoami, access_token, username, password)
    success_login = account_login(whoami, access_token)
    if success_login:
        return True


def account_login(whoami, access_token):
    # def account_login(whoami, access_token, username, password):
    # get username and password
    username = click.prompt('Enter username', type=str).strip().lower()
    password = click.prompt('Enter password', type=str)

    # print('account_login\n')
    """fetch from database"""
    try:
        account = db.Accounts.find_one(
            {f'{whoami}.username': username},
            {f'{whoami}.$': 1}
        )

        if account:
            extract_password = {
                'password': account[whoami][0]['password']
            }

            # check hash password
            if bcrypt.checkpw(password.encode(), extract_password['password']):
                click.echo('Login Successfully')
            else:
                click.echo('please Enter correct password')
                # if password not match exit
                return

            # print('CALL mac_address\n')
            mac_address = device_mac_address()
            # print(f'BACK mac_address: {mac_address}\n')

            EXP_DATE = timedelta(days=30)
            payload = {
                'account': whoami,
                'id': account[whoami][0]['id'],
                'device': mac_address,
                'iat': int(datetime.now().timestamp()),
                'exp': int((datetime.now() + EXP_DATE).timestamp())
            }

            # encrypt access_token
            # print('Call enocde_access_token\n')
            check = encode_access_token(payload, access_token)
            # print(f'BACK enocde_access_token: {check}\n')
            if not check:
                return

            # print('CALL refresh_token\n')
            refresh_token(access_token)
            # print('BACK refresh_token\n')

            # print("SUCCESSFULLY LOGIN")
            return True
        else:
            click.echo('Account not found')
            return
    except KeyboardInterrupt:
        click.echo('exiting...')
    except Exception as e:
        logger.error(e)
        click.echo(f'Got Exception in login: {e}')
        return


# get macaddress from device
def device_mac_address():
    # print('INSIDE device_mac_address\n')
    mac_address = ''
    device = '/sys/class/net/enp1s0/address'
    with open(device, 'r') as file:
        mac_address = file.readline().strip()
        # print(f'RETURN mac_address: {mac_address}\n')
        return mac_address


def _count_accounts(category):
    try:
        account = db.Accounts.aggregate([
            {
                '$match': {f'{category}': {'$exists': True}}
            },
            {
                '$project': {
                    '_id': 0,
                    'count': {'$size': f'${category}'}
                }
            }
        ]).next()['count']

        id = account + 1
        return id
    except StopIteration:
        return 1


def encode_access_token(json_text, access_token):
    # print('INSIDE encode_access_token')
    SECRET_KEY = os.getenv(access_token)
    ALGORITHM = 'HS256'

    encrypted_text = jwt.encode(json_text, SECRET_KEY, algorithm=ALGORITHM)
    data_dir = data_path('access_token')

    with open(data_dir, 'w') as file:
        json.dump(encrypted_text, file)
        # print('RETURN from encode_access_token')
        return True


def dencode_access_token(access_token):
    from config import get_access_token

    SECRET_KEY = os.getenv(access_token)
    token = get_access_token()
    if not token:
        return

    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256'],
            options={
                'require': ['exp'],
                'verify_exp': ['exp']
            })
        return decoded

    except jwt.exceptions.ExpiredSignatureError:
        click.echo('Your Token is Expired, Login Again..')
        # logmeout()
        return

    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        click.echo('Your Token is invalid, Login Again..')
        # logmeout()
        return

    except Exception as e:
        logger = logging_module()
        logger.debug(e)
        return


def refresh_token(access_token):
    # print('INSIDE refresh_token')
    try:
        # decrypt token
        data_json = dencode_access_token(access_token)

        if not data_json:
            return

        # check mac of device is same or not
        device = data_json['device']
        # print(f"CALL MAC ADDRESS FROM refresh_token{device}\n")
        address = device_mac_address()
        # print(f"RETURN MAC ADDRESS FROM refresh_token{address}\n")
        if device != address:
            logout()
            click.echo('Your Token is Invalid')
            return

        # check whose access token is it (admin/user)
        account = data_json['account']
        id = data_json['id']

        accounts = db.Accounts.find_one(
                {f'{account}.id': id},
                {f'{account}.$': 1}
            )
        # get username
        # print(f'Accounts in refresh_token: {list(accounts)}')

        username = accounts[account][0]['username']
        token = ''
        data_dir = ''

        if account == 'Admin':
            secret = 'jwt_admin_secret'
            data_dir = data_path('admin')
            email = ''
            # print('CALL generate_token\n')
            token = generate_token(username, secret, email)
            # print(f'AFTER generate_token: {token}\n')
            # if not token:
            #     return

        elif account == 'User':
            secret = 'jwt_user_secret'
            data_dir = data_path('user')
            email = accounts[account][0]['email']
            # print('CALL generate_token')
            token = generate_token(username, secret, email)
            # print(f'AFTER generate_token: {token}\n')
            # if not token:
            #     return

        # after condition check then save in file
        with open(data_dir, 'w') as file:
            json.dump(token, file)
            # print(f'written REFRESH_TOKEN to File{token}\n')
    except Exception as e:
        logger.error(e)
        return
    # return False


def generate_token(username, secret, email):
    # print('INSIDE generate_token')
    SECRET_KEY = os.getenv(secret)
    ALGORITHM = 'HS256'
    EXP_DATE = timedelta(minutes=1)
    payload = {}

    try:
        if secret == 'jwt_user_secret':
            payload = {
                'username': username,
                'email': email,
                'iat': int(datetime.now().timestamp()),
                'exp': int((datetime.now() + EXP_DATE).timestamp())
            }

        elif secret == 'jwt_admin_secret':
            payload = {
                'username': username,
                'iat': int(datetime.now().timestamp()),
                'exp': int((datetime.now() + EXP_DATE).timestamp())
            }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        if token:
            # print(f'RETURN token: {token}')
            return token
    except Exception as e:
        logger.error(e)
        return

    # return False


if __name__ == '__main__':
    admin_login()
