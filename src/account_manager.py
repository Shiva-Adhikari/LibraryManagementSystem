# third party modules
import jwt
import bcrypt
from pydantic import ValidationError
from password_validator import PasswordValidator  # type: ignore
from email_validator import validate_email, EmailNotValidError

# built in modules
from datetime import datetime, timedelta  # combine is better

# local modules
from src.utils import (
    logger,
    _read_json, _send_response
)
from src.models import AccountRegisterModel, settings, db


def email_validation(handler, _email):
    """Validate email address

    Returns:
        str: if email validate then return email.
    """

    try:
        email = validate_email(_email, check_deliverability=False)
        email = email.normalized
        return email
    except EmailNotValidError as e:

        response = {'error': f'Email not Valid {str(e)}'}
        _send_response(handler, response, 500)
        return


def password_validation(handler, password: str):
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
            messages = 'Password must be 8+ characters with upper, lower, '
            'digit, and special symbols.'
            response = {'error': messages}
            _send_response(handler, response, 500)
            return
    except Exception as e:
        response = {'error': f'Password not valid: {str(e)}'}
        _send_response(handler, response, 500)
        return None


def confirm_password_validation(handler, _password):
    """Validate 'password' and 'confirm password'

    Returns:
        str: Return password
    """

    password = password_validation(handler, _password)
    if not password:
        return

    # create salt
    salt = bcrypt.gensalt(rounds=10)
    # convert password to hash with added salt
    password = bcrypt.hashpw(password.encode(), salt)
    return password


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

    return bool(check_account)


def validation(handler, admin, username, _password):
    """Validate Account

    Args:
        admin (str): Try to fetch Credentials

    Returns:
        tuple[str, str]: Return Credentials ( username, password )
    """

    if len(username) > 3:
        account = check_accounts(admin, username)
        if account:
            response = {'error': 'Username exits check another'}
            _send_response(handler, response, 500)
            return
    else:
        response = {'error': 'username must be more than 4 letter long'}
        _send_response(handler, response, 500)

    password = confirm_password_validation(handler, _password)
    if not password:
        return
    return username.lower(), password


def account_register(handler, whoami):
    """User and Admin account register

    Args:
        whoami (str): it define whether User or Admin try to register account.
    """

    try:
        data = _read_json(handler)
        _username = data.get('username').lower().strip()
        _password = data.get('password')
        _email = data.get('email', '').lower().strip()

        username, password = validation(handler, whoami, _username, _password)
        id = _count_accounts(whoami)

        account_data = {
            'username': username,
            'password': password,
        }

        if whoami == 'User':
            email = email_validation(handler, _email)
            if not email:
                return

            account_data['email'] = email

        validated_data = AccountRegisterModel(**account_data)
        _email = validated_data.email if whoami == 'User' else None

        add_accounts = db.Accounts.update_one(
            {f'{whoami}': {'$exists': True}},
            {'$push': {
                f'{whoami}': {
                    'id': id,
                    'username': validated_data.username,
                    'email': _email,
                    'password': validated_data.password
                }
            }},
            upsert=True
        )

        if add_accounts.modified_count > 0 or add_accounts.upserted_id:
            response = {
                'message': 'Successfully Registered Account',
                'account': username,
            }
            _send_response(handler, response, 200)
            return True

        else:
            logger.debug('Register Failed')
            response = {
                'error': 'Register Failed',
                'account': username,
            }
            _send_response(handler, response, 500)
            return

    except ValidationError as ve:
        response = {
            'error': f'Invalid Input: {ve}',
            'account': username,
        }
        _send_response(handler, response, 500)
        return

    except Exception as e:
        logger.error(e)
        return


def account_login(handler, whoami, SECRET_KEY):
    """User or Admin account login

    Args:
        whoami (str): This is where user or admin login
        access_token (str): This is a text where it identifies User or
                            Admin login and get secret key from .env file.

    Returns:
        bool: if successfully written in file it return True
    """

    data = _read_json(handler)
    username = data.get('username').lower().strip()
    password = data.get('password')

    try:
        account = db.Accounts.find_one(
            {f'{whoami}.username': username},
            {f'{whoami}.$': 1}
        )

        if account:
            extract_password = {
                'password': account[whoami][0]['password']
            }
            _extract_password = extract_password['password'].encode('utf-8')

            # check hash password
            if not bcrypt.checkpw(password.encode(), _extract_password):
                response = {'error': 'please enter correct password'}
                _send_response(handler, response, 500)
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
            _access_token = encode_access_token(handler, payload, SECRET_KEY)
            if not _access_token:
                logger.error()
                return

            _, _refresh_token = refresh_token(
                handler, _access_token, SECRET_KEY)
            if not _refresh_token:
                logger.error()
                return

            response = {
                'status': 'success',
                'account': username,
                'access token': _access_token,
                'refresh token': _refresh_token
            }
            _send_response(handler, response, 200)

            return True
        else:
            response = {'error': 'Account not found'}
            _send_response(handler, response, 500)
            return

    except Exception as e:
        logger.error(e)
        return


# get macaddress from device
def device_mac_address():
    """Fetch macaddress from linux machine

    Returns:
        str: return macaddress.
    """

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
            }, {
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


def encode_access_token(handler, json_text, SECRET_KEY):
    """Convert Text to access_token

    Args:
        json_text (str): User credentials
        access_token (str): it is a token where it fetch token from .env

    Returns:
        True: if encoded token is successfully written in file.
    """

    ALGORITHM = settings.JWT_ALGORITHM.get_secret_value()

    encrypted_text = jwt.encode(json_text, SECRET_KEY, algorithm=ALGORITHM)

    if encrypted_text:
        return encrypted_text


def dencode_access_token(handler, encoded_access_token, SECRET_KEY):
    """Decode access token which is get from file

    Args:
        SECRET_KEY (str): This is a secret key to decode token

    Returns:
        str: if successfully decoded then it return decoded text
    """

    ALGORITHM = settings.JWT_ALGORITHM.get_secret_value()
    try:
        decoded = jwt.decode(
            encoded_access_token,
            SECRET_KEY,
            algorithms=ALGORITHM,
            options={
                'require': ['iat', 'exp'],
                'verify_iat': ['iat'],
                'verify_exp': ['exp']
            })

        if decoded:
            return decoded

    except jwt.exceptions.ExpiredSignatureError:
        response = {'token error': 'Your Token is Expired, Login Again.'}
        _send_response(handler, response, 400)

    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        response = {'token error': 'Your Token is invalid, Login Again.'}
        _send_response(handler, response, 400)

    except Exception as e:
        logger.debug(e)


def refresh_token(handler, encoded_access_token, SECRET_KEY):
    """A refresh token used to refresh the expired token

    Args:
        access_token (str): This is secret key to decode and encode.
    """

    try:
        data_json = dencode_access_token(
            handler, encoded_access_token, SECRET_KEY)

        if not data_json:
            logger.error('unable to decode_access_token')
            return

        device = data_json['device']
        address = device_mac_address()
        if device != address:
            response = {'mac-address': 'Your Token is Invalid'}
            _send_response(handler, response, 500)
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

        if account == 'Admin':
            SECRET_KEY = settings.ADMIN_SECRET_JWT.get_secret_value()
            email = ''
            token, payload = generate_token(
                username, SECRET_KEY, email, account)

        elif account == 'User':
            SECRET_KEY = settings.USER_SECRET_JWT.get_secret_value()
            email = accounts[account][0]['email']
            token, payload = generate_token(
                username, SECRET_KEY, email, account)

        if (payload or token):
            return payload, token

    except Exception as e:
        logger.error(e)
        return


def generate_token(username, SECRET_KEY, email, account):
    """This is used to create token used to encode
        user credentials i.e username and email

    Args:
        username (str): This is a username of User or Admin
        secret (str): This is a secret key to encode
        email (str): User email address

    Returns:
        str: if succesfully encoded then it return.
    """

    ALGORITHM = settings.JWT_ALGORITHM.get_secret_value()
    EXP_DATE = timedelta(days=5)
    payload = {}

    try:
        payload = {
            'username': username,
            'email': email if account == 'User' else None,
            'iat': int(datetime.now().timestamp()),
            'exp': int((datetime.now() + EXP_DATE).timestamp())
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        if token:
            return token, payload

    except Exception as e:
        logger.error(e)
