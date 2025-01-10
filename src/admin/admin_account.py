import click
import json
from pymongo import MongoClient
from password_validator import PasswordValidator

from config import data_path


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
            return password
        else:
            click.echo('password not match')


def validation() -> tuple[str, str]:
    """get username and return with password"""
    username = click.prompt('Enter Username: ', type=str)
    password = confirm_password_validation()
    return username, password


def get_next_sequence_value(sequence_name: str, db):
    """Auto increment user_id"""
    counter = db.counters.find_one_and_update(
        # find the document with the sequence name eg. 'user_id'all
        {'+_id': sequence_name},
        # increment seq by 1
        {'$inc': {'seq': 1}},
        # if not found, create the document with 1
        upsert=True,
        # return the updated document
        return_document=True
    )
    # return the updated vlaue of seq ( the next unique ID)
    return counter['seq']


def admin_register():
    """save in database"""
    try:
        username, password = validation()
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        # next_id = get_next_sequence_value('admin_id', db)
        add_accounts = db.Accounts.update_one(
            {'Admin': {'$exists': True}},
            {'$push': {
                'Admin': {
                    'username': username,
                    'password': password
                }
            }},
            upsert=True
        )
        if add_accounts.modified_count > 0 or add_accounts.upserted_id:
            click.echo('Register Successfully')
        else:
            # ADD LOGGING HERE
            click.echo('Register Failed')
    except Exception as e:
        click.echo(f'Got Exception in admin_register: {e}')


def admin_login():
    username = click.prompt('Enter username: ', type=str)
    password = click.prompt('Enter password: ', type=str)
    """fetch from database"""
    try:
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        admin = db.Accounts.find_one({
            'Admin.username': username,
            'Admin.password': password
        })
        if admin:
            click.echo('Login Successfully')
            extract_user = {
                'username': admin['Admin'][0]['username'],
            }
            data_dir = data_path('admin')
            with open(data_dir, 'w') as file:
                json.dump(extract_user, file)
            return admin
        else:
            click.echo('Account not found')
    except Exception as e:
        # ADD LOGGING HERE
        click.echo(f'Got Exception in admin_register: {e}')


# if __name__ == '__main__':
    #     pass
    # admin_register()
    # admin_login()
