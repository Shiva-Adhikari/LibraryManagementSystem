from email_validator import validate_email, EmailNotValidError
import click
from src.admin.admin_account import validation
from pymongo import MongoClient


def email_validation() -> str:
    while True:
        email = click.prompt('Enter Email: ', type=str)
        try:
            email = validate_email(email, check_deliverability=False)
            email = email.normalized
            return email
        except EmailNotValidError as e:
            print(str(e))


def user_register():
    try:
        email = email_validation()
        username, password = validation()
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        add_accounts = db.Accounts.update_one(
            {'User': {'$exists': True}},
            {'$push': {
                'User': {
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
            # ADD LOGGING HERE
            click.echo('Register Failed')
    except Exception as e:
        # ADD LOGGING HERE
        click.echo(f'Got Exception in user_register: {e}')


def user_login():
    username = click.prompt('Enter username: ', type=str)
    email = click.prompt('Enter email: ', type=str)
    password = click.prompt('Enter password: ', type=str)
    """fetch from database"""
    try:
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        user = db.Accounts.find_one({
            'User.username': username,
            'User.email': email,
            'User.password': password
        }, {'User.$': 1}  # get only 1 specific match element
        )
        if user:
            click.echo('Login Successfully')
            user_details(user)
        else:
            click.echo('Account not found')
    except Exception as e:
        # ADD LOGGING HERE
        click.echo(f'Got Exception in admin_register: {e}')


def user_details(user):
    """get user credentials"""
    return user


if __name__ == '__main__':
    pass
    # user_register()
    # user_login()
