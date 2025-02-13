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
from cryptography.fernet import Fernet
from email_validator import validate_email, EmailNotValidError


# import from file
from config import data_path
from config import logging_module

# from src.user.user_account import email_validation


# start_id = 1

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
                {'User': {'$exists': True}},
                {'$push': {
                    'User': {
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
    account_login(whoami)


def account_login(whoami):
    username = click.prompt('Enter username', type=str).strip().lower()
    password = click.prompt('Enter password', type=str)
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

            # EXP_DATE = timedelta(minutes=5)   ###############
            _access_token = {
                'account': whoami,
                'id': account[whoami][0]['id'],
                # 'device': insert_device_mac_address   ###############
                # 'exp': int((datetime.now() + EXP_DATE).timestamp())   ###############
            }

            print('access_token')

            # encrypt access_token
            check = encrypt_text(_access_token)
            if not check:
                print('not check')
                print('exiting..')
                return

            refresh_token()
            print('encrypt_text done')

            return True
        else:
            click.echo('Account not found')
            return False
    except KeyboardInterrupt:
        click.echo('exiting...')
    except Exception as e:
        logger.error(e)
        click.echo(f'Got Exception in admin login: {e}')
        return False


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


def encrypt_text(text):
    SECRET_KEY_FERNET = os.getenv('SECRET_KEY_FERNET')

    # create fernet instance (object)
    fernet = Fernet(SECRET_KEY_FERNET)

    # convert dictionary into json formatted data
    # now it becomes string and now successfully encoded
    json_text = json.dumps(text)

    print(f'json_text: {json_text}')
    encrypted_text = fernet.encrypt(json_text.encode()).decode()
    data_dir = data_path('access_token')
    print(f'encrypted_text: {encrypted_text}')

    with open(data_dir, 'w') as file:
        json.dump(encrypted_text, file)
        return True
    return False


def decrypt_text():
    SECRET_KEY_FERNET = os.getenv('SECRET_KEY_FERNET')
    # create fernet instance (object)
    fernet = Fernet(SECRET_KEY_FERNET)
    data_dir = data_path('access_token')
    print('hello')

    with open(data_dir, 'r') as file:
        print("hello1")
        text = json.load(file)
        print(f'text: {text}')

    print("hello2")
    decrypted_text = fernet.decrypt(text.encode()).decode()
    print(f'decrypted_text: {decrypted_text}')
    return decrypted_text


def refresh_token():
    # decrypt token
    data_dict = decrypt_text()
    # convert into json file from dictionary
    data_json = json.loads(data_dict)
    # check whose access token is it (admin/user)
    account = data_json['account']
    id = data_json['id']
    print(f"data account: {data_json['account']}")
    print(f"data id: {data_json['id']}")

    accounts = db.Accounts.find_one(
            {f'{account}.id': id},
            {f'{account}.$': 1}
        )

    # get username
    username = accounts[account][0]['username']
    print(f'username: {username}')
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
        print('successfully dump token')


def generate_token(username, secret, email):
    SECRET_KEY = os.getenv(secret)
    ALGORITHM = 'HS256'
    EXP_DATE = timedelta(minutes=5)
    payload = {}

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

    print(f'generate_token payload: {payload}')
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f'generate_token token: {token}')
    return token


if __name__ == '__main__':
    # admin_register()
    admin_login()
    # refresh_token()
    # encrypt_text()
    # decrypt_text()
