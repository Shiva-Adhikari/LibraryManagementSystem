# from pymongo import MongoClient
from password_validator import PasswordValidator
import click


def password_validation(password: str) -> str:
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
            click.echo('Password must be 8+ characters with upper, lower, digit, and special symbols.')
    except Exception as e:
        click.echo(f'Password not valid: {str(e)}')
        return None


def confirm_password_validation():
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
            return password
        else:
            click.echo('password not match')


def validation():
    """get username and return with password"""
    username = click.prompt('Enter Username: ', type=str)
    password = confirm_password_validation()
    return username, password


def admin_register():
    """save in database"""
    username, password = validation()
    print(f'username: {username}')
    print(f'password: {password}')


def admin_login():
    """fetch from database"""
    pass


def main():
    admin_register()


if __name__ == '__main__':
    main()
