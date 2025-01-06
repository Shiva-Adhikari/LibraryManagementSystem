# from admin import password_validation
from email_validator import validate_email, EmailNotValidError
import click
from .admin import validation
from .admin import get_next_sequence_value
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
        next_id = get_next_sequence_value('user_id', db)
        db.user.insert_one({
            '_id': next_id,
            'username': username,
            'email': email,
            'password': password
        })
    except Exception as e:
        click.echo(f'Got Exception in user_register: {e}')


def user_login():
    username = click.prompt('Enter username: ', type=str)
    email = click.prompt('Enter email: ', type=str)
    password = click.prompt('Enter password: ', type=str)
    """fetch from database"""
    try:
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        admin = db.user.find_one({
            'username': username, 'email': email, 'password': password
        })
        if admin:
            print(f'found: {admin}')
        else:
            print(f'not found {admin}')
    except Exception as e:
        click.echo(f'Got Exception in admin_register: {e}')


def main():
    validation()


if __name__ == '__main__':
    main()
