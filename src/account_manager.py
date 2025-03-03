# third party modules
import jwt
import click
import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import ValidationError
from password_validator import PasswordValidator
from email_validator import validate_email, EmailNotValidError

# built in modules
import os
import json
from datetime import datetime, timedelta  # combine is better

# local modules
from src.utils import logout
from src.utils import data_path
from src.utils import logging_module
from src.models.account_model import AccountRegisterModel


logger = logging_module()

src_path = os.path.join('src')
env_path = os.path.join(src_path, '.env')
load_dotenv(env_path)

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def email_validation() -> str:
    """Validate email address

    Returns:
        str: if email validate then return email.
    """
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
    """Validate Combination of password

    Args:
        password (str): This is password to validate

    Returns:
        str: if combination password validate it return password.
    """
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
    """Validate 'password' and 'confirm password'

    Returns:
        str: Return password
    """
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
    """Check Account whether Account is available or not

    Args:
        account (str): Admin or User account
        username (str): username

    Returns:
        bool: if account match it return True.
    """
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
    """Validate Account

    Args:
        admin (str): Try to fetch Credentials

    Returns:
        tuple[str, str]: Return Credentials ( username, password )
    """
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


def account_register(whoami):
    """User and Admin account register

    Args:
        whoami (str): it define whether User or Admin try to register account.
    """
    try:
        username, password = validation(whoami)
        id = _count_accounts(whoami)
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem

        account_data = {
            'username': username,
            'password': password,
        }

        if whoami == 'User':
            email = email_validation()
            if not email:
                return
            account_data['email'] = email

        validated_data = AccountRegisterModel(**account_data)

        add_accounts = db.Accounts.update_one(
            {f'{whoami}': {'$exists': True}},
            {'$push': {
                f'{whoami}': {
                    'id': id,
                    'username': validated_data.username,
                    'email': validated_data.email if whoami == 'User' else None,
                    'password': validated_data.password
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

    except ValidationError as ve:
        click.echo(f'Invalid Input: {ve}')

    except Exception as e:
        logger.error(e)
        click.echo(f'Got Exception in register: {e}')
        return


def account_login(whoami, access_token):
    """User or Admin account login

    Args:
        whoami (str): This is where user or admin login
        access_token (str): This is a text where it identifies User or
                            Admin login and get secret key from .env file.

    Returns:
        bool: if successfully written in file it return True
    """
    username = click.prompt('Enter username', type=str).strip().lower()
    password = click.prompt('Enter password', type=str)

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

            mac_address = device_mac_address()

            EXP_DATE = timedelta(days=30)
            payload = {
                'account': whoami,
                'id': account[whoami][0]['id'],
                'device': mac_address,
                'iat': int(datetime.now().timestamp()),
                'exp': int((datetime.now() + EXP_DATE).timestamp())
            }

            # encrypt access_token
            check = encode_access_token(payload, access_token)
            if not check:
                return

            refresh_token(access_token)
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
    """Fetch macaddress from linux machine

    Returns:
        str: return macaddress.
    """
    mac_address = ''
    device = '/sys/class/net/enp1s0/address'
    with open(device, 'r') as file:
        mac_address = file.readline().strip()
        return mac_address


def _count_accounts(category):
    """Used to insert id.

    Args:
        category (str): Admin or User

    Returns:
        int: Assign the id.
    """
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
    """Convert Text to access_token

    Args:
        json_text (str): User credentials
        access_token (str): it is a token where it fetch token from .env

    Returns:
        True: if encoded token is successfully written in file.
    """
    SECRET_KEY = os.getenv(access_token)
    ALGORITHM = 'HS256'

    encrypted_text = jwt.encode(json_text, SECRET_KEY, algorithm=ALGORITHM)
    data_dir = data_path('access_token')

    with open(data_dir, 'w') as file:
        json.dump(encrypted_text, file)
        return True


def dencode_access_token(access_token):
    """Decode access token which is get from file

    Args:
        access_token (str): This is a secret key to decode token

    Returns:
        str: if successfully decoded then it return decoded text
    """
    from src.utils import get_access_token

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
        logout()
        return

    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        click.echo('Your Token is invalid, Login Again..')
        logout()
        return

    except Exception as e:
        logger = logging_module()
        logger.debug(e)
        return


def refresh_token(access_token):
    """A refresh token used to refresh the expired token

    Args:
        access_token (str): This is secret key to decode and encode.
    """
    try:
        # decrypt token
        data_json = dencode_access_token(access_token)

        if not data_json:
            return

        # check mac of device is same or not
        device = data_json['device']
        address = device_mac_address()
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
        username = accounts[account][0]['username']
        token = ''
        data_dir = ''

        if account == 'Admin':
            secret = 'jwt_admin_secret'
            data_dir = data_path('admin')
            email = ''
            token = generate_token(username, secret, email)

        elif account == 'User':
            secret = 'jwt_user_secret'
            data_dir = data_path('user')
            email = accounts[account][0]['email']
            token = generate_token(username, secret, email)

        # after condition check then save in file
        with open(data_dir, 'w') as file:
            json.dump(token, file)
            return True
    except Exception as e:
        logger.error(e)
        return


def generate_token(username, secret, email):
    """This is used to create token used to encode
        user credentials i.e username and email

    Args:
        username (str): This is a username of User or Admin
        secret (str): This is a secret key to encode
        email (str): User email address

    Returns:
        str: if succesfully encoded then it return.
    """
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
            return token
    except Exception as e:
        logger.error(e)
        return
