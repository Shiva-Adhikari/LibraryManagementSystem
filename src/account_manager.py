# third party modules
import jwt
import bcrypt
from pydantic import ValidationError
from password_validator import PasswordValidator  # type: ignore
from email_validator import validate_email, EmailNotValidError

# built in modules
from datetime import datetime, timedelta

# local modules
from src.utils import logger, _read_json, _send_response, Env
from src.models import Account, AccountDetails


@_send_response
def email_validation(self, _email):
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
        return (response, 400)


@_send_response
def password_validation(self, password: str):
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
            return (response, 400)
    except Exception as e:
        response = {'error': f'Password not valid: {str(e)}'}
        return (response, 400)


def confirm_password_validation(self, _password: str):
    """Validate 'password' and 'confirm password'

    Returns:
        str: Return password
    """

    password = password_validation(self, _password)
    if not password:
        return

    # create salt
    salt = bcrypt.gensalt(rounds=10)
    # convert password to hash with added salt
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode('utf-8')


def check_accounts(account, username: str):
    """Check Account whether Account is available or not

    Args:
        account (str): Admin or User account
        username (str): username

    Returns:
        bool: if account match it return True.
    """

    account = Account.objects(account=account).first()
    if not account:
        return

    account_ids = []
    for acc in account.account_details:
        account_ids.append(acc.id)

    account_details = AccountDetails.objects(
        username=username, id__in=account_ids).first()
    return bool(account_details)


@_send_response
def validation(self, admin: str, username: str, _password: str):
    """Validate Account

    Args:
        admin (str): Try to fetch Credentials

    Returns:
        tuple[str, str]: Return Credentials ( username, password )
    """

    if len(username) > 3:
        account = check_accounts(admin, username)
        if account:
            response = {'error': 'Same username found. Not adding again.1'}
            return (response, 409)
    else:
        response = {'error': 'username must be more than 4 letter long'}
        return (response, 400)

    password = confirm_password_validation(self, _password)
    if not password:
        return

    user_pass = {
        'username': username.lower(),
        'password': password
    }
    return user_pass


@_send_response
@_read_json
def account_register(self, data, whoami: str):
    """User and Admin account register

    Args:
        whoami (str): it define whether User or Admin try to register account.
    """

    try:
        _username = data.get('username').lower().strip()
        _password = data.get('password')
        _email = data.get('email', '').lower().strip()

        data = validation(self, whoami, _username, _password)
        if not data:
            response = {
                'status': 'error',
                'message': 'Same username found. Not adding again.2',
            }
            return (response, 409)

        username = data.get('username')
        password = data.get('password')
        account_data = {
            'username': username,
            'password': password,
        }
        if whoami == 'User':
            email = email_validation(self, _email)
            if not email:
                return
            account_data['email'] = email

        validated_data = AccountDetails(**account_data)
        try:
            validated_data.save()
        except Exception:
            response = {
                'status': 'error',
                'message': 'Same username found. Not adding again.3',
            }
            return (response, 409)

        # account bane ko xaina vane naya banaune
        account = Account.objects(account=whoami).first()
        if not account:
            account = Account(account=whoami, account_details=[])
            account.save()

        # Append AccountDetails & Save
        account.account_details.append(validated_data)
        account.save()

        response = {
            'account': username,
            'message': 'Successfully Registered Account',
        }
        return (response, 201)
    except ValidationError as ve:
        response = {
            'error': f'Invalid Input: {ve}',
            'account': username,
        }
        return (response, 400)

    except Exception as e:
        return logger.error(e)


@_send_response
@_read_json
def account_login(self, data, whoami: str, SECRET_KEY: str):
    """User or Admin account login

    Args:
        whoami (str): This is where user or admin login
        access_token (str): This is a text where it identifies User or
                            Admin login and get secret key from .env file.

    Returns:
        bool: if successfully written in file it return True
    """
    if not data:
        return
    username = data.get('username').lower().strip()
    password = data.get('password')
    try:
        account = AccountDetails.objects(username=username).first()
        if account:
            extract_password = account.password
            _extract_password = extract_password.encode('utf-8')

            # check hash password
            if not bcrypt.checkpw(password.encode(), _extract_password):
                response = {'error': 'please enter correct password'}
                return (response, 400)

            mac_address = device_mac_address()
            EXP_DATE = timedelta(days=30)
            payload = {
                'account': whoami,
                'id': str(account.id),
                'device': mac_address,
                'iat': int(datetime.now().timestamp()),
                'exp': int((datetime.now() + EXP_DATE).timestamp())
            }

            # encrypt access_token
            _access_token = encode_access_token(payload, SECRET_KEY)
            if not _access_token:
                return logger.error()

            token = refresh_token(self, _access_token, SECRET_KEY)
            _refresh_token = token['token']
            if not _refresh_token:
                return logger.error()

            response = {
                'status': 'success',
                'account': username,
                'access token': _access_token,
                'refresh token': _refresh_token
            }
            return (response, 200)
        else:
            response = {'error': 'Account not found'}
            return (response, 404)

    except Exception as e:
        return logger.error(e)


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


def encode_access_token(json_text, SECRET_KEY: str):
    """Convert Text to access_token

    Args:
        json_text (str): User credentials
        access_token (str): it is a token where it fetch token from .env

    Returns:
        True: if encoded token is successfully written in file.
    """

    ALGORITHM = Env.JWT_ALGORITHM.value

    encrypted_text = jwt.encode(json_text, SECRET_KEY, algorithm=ALGORITHM)

    if encrypted_text:
        return encrypted_text


@_send_response
def dencode_access_token(self, encoded_access_token: str, SECRET_KEY: str):
    """Decode access token which is get from file

    Args:
        SECRET_KEY (str): This is a secret key to decode token

    Returns:
        str: if successfully decoded then it return decoded text
    """

    ALGORITHM = Env.JWT_ALGORITHM.value
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
        return (response, 400)

    except (jwt.exceptions.InvalidTokenError, jwt.DecodeError):
        response = {'token error': 'Your Token is invalid, Login Again.'}
        return (response, 400)

    except Exception as e:
        return logger.debug(e)


@_send_response
def refresh_token(self, encoded_access_token, SECRET_KEY: str):
    """A refresh token used to refresh the expired token

    Args:
        access_token (str): This is secret key to decode and encode.
    """

    try:
        data_json = dencode_access_token(
            self, encoded_access_token, SECRET_KEY)
        if not data_json:
            return logger.error('unable to decode_access_token')

        device = data_json['device']
        address = device_mac_address()
        if device != address:
            response = {'mac-address': 'Your Token is Invalid'}
            return (response, 401)

        # check whose access token is it (admin/user)
        account = data_json['account']
        id = data_json['id']

        accounts = AccountDetails.objects(id=id).first()
        # get username
        username = accounts.username
        if account == 'Admin':
            SECRET_KEY = Env.ADMIN_SECRET_JWT.value
            email = ''
            token, payload = generate_token(
                username, SECRET_KEY, email, account)

        elif account == 'User':
            SECRET_KEY = Env.USER_SECRET_JWT.value
            email = accounts.email
            token, payload = generate_token(
                username, SECRET_KEY, email, account)

        if (payload or token):
            send_me = {
                'payload': payload,
                'token': token
            }
            return send_me

    except Exception as e:
        return logger.error(e)


def generate_token(username, SECRET_KEY: str, email: str, account: str):
    """This is used to create token used to encode
        user credentials i.e username and email

    Args:
        username (str): This is a username of User or Admin
        secret (str): This is a secret key to encode
        email (str): User email address

    Returns:
        str: if succesfully encoded then it return.
    """

    ALGORITHM = Env.JWT_ALGORITHM.value
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
        return logger.error(e)
