# from pymongo import MongoClient
from password_validator import PasswordValidator
import click
from pymongo import MongoClient


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
        {'+_id': sequence_name},    # find the document with the sequence name eg. 'user_id'all
        {'$inc': {'seq': 1}},   # increment seq by 1
        upsert=True,    # if not found, create the document with 1
        return_document=True    # return the updated document
    )
    return counter['seq']   # return the updated vlaue of seq ( the next unique ID)


def admin_register():
    """save in database"""
    try:
        username, password = validation()
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        next_id = get_next_sequence_value('admin_id', db)
        db.admin.insert_one({
            '_id': next_id,
            'username': username,
            'password': password
        })
        click.echo('Successfully saved')
    except Exception as e:
        click.echo(f'Got Exception in admin_register: {e}')


def admin_login():
    """fetch from database"""
    pass


def main():
    admin_register()


if __name__ == '__main__':
    main()
