import json
import click
import bcrypt
from pymongo import MongoClient
from email_validator import validate_email, EmailNotValidError

from config import data_path
from config import logging_module
from src.admin.admin_account import validation


logger = logging_module()


def email_validation() -> str:
    while True:
        email = click.prompt('Enter Email: ', type=str)
        try:
            email = validate_email(email, check_deliverability=False)
            email = email.normalized
            return email
        except EmailNotValidError as e:
            click.echo(str(e))


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
            logger.error('Register Failed')
            click.echo('Register Failed')
    except KeyboardInterrupt:
        click.echo('exiting...')
    except Exception as e:
        logger.error(f'{str(e)}')
        click.echo(f'Got Exception in user_register: {e}')


def user_login():
    username = click.prompt('Username: ', type=str)
    password = click.prompt('Password: ', type=str)
    """user credential from database"""
    try:
        client = MongoClient('localhost', 27017)
        db = client.LibraryManagementSystem
        user = db.Accounts.find_one(
            {'User.username': username},
            {'User.$': 1}
        )
        if user:
            extract_password = {
                'password': user['User'][0]['password']
            }
            if bcrypt.checkpw(password.encode(), extract_password['password']):
                click.echo('Login Successfully')
            else:
                click.echo('please Enter correct password')
            extract_username_email = {
                'username': user['User'][0]['username'],
                'email': user['User'][0]['email']
            }
            data_dir = data_path('user')
            with open(data_dir, 'w') as file:
                json.dump(extract_username_email, file)
            return user
        else:
            click.echo('Account not found')
    except KeyboardInterrupt:
        click.echo('exiting...')
    except Exception as e:
        logger.error(f'{str(e)}')
        click.echo(f'Got Exception in user_login: {e}')
