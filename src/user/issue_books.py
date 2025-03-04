# third party modules
import click
# from pymongo import MongoClient

# built in modules
import time
from datetime import datetime
from datetime import timedelta

# local modules
from src.utils import logger
from src.utils import verify_jwt_token
from src.admin.stock_book import find_keys
from src.models.settings import db


def issue_books() -> None:
    """User issue book.
    """
    # check if books is empty or not
    check_books = find_keys()
    if not check_books:
        click.echo('Books Not found, exiting...')
        time.sleep(2)
        return
    # user input
    input_categories = click.prompt('Enter Book Category', type=str).lower()
    input_book_name = click.prompt('Enter Book Name', type=str).lower()
    to_date = click.prompt('For how many days you need', type=int)

    try:
        input_categories = input_categories.lower()
        issue_date = datetime.now()
        warning_to_date = to_date - 3
        due_warning = issue_date + timedelta(days=warning_to_date)
        due_date = issue_date + timedelta(days=to_date)

        user_detail = verify_jwt_token()
        if not user_detail:
            time.sleep(1)
            return

        username = user_detail['username']
        email = user_detail['email']

        does_exist = validate_user(input_categories, input_book_name, username)
        if does_exist:
            click.echo('Book is already Issue, unable to issue again.')
            time.sleep(2)
            return

        result = db.Books.update_one(
            {f'{input_categories}.Title': input_book_name},
            {
                '$inc': {
                    f'{input_categories}.$.Available': -1
                },

                '$push': {
                    f'{input_categories}.$.UserDetails':
                        {
                            'Username': username,
                            'Email': email,
                            'Days': to_date,
                            'IssueDate': issue_date,
                            'DueWarning': due_warning,
                            'DueDate': due_date,
                        }

                }
            }
        )

        if result.modified_count > 0:
            click.echo('You got book')
        else:
            click.echo('Unable to get book, Try Again.')

    except Exception as e:
        logger.error(e)
        click.echo(f"got exception as {str(e)}")


def validate_user(input_categories, input_book_name, username):
    """check book is available or not in Database

    Args:
        input_categories (str): Book Category
        input_book_name (str): user input Book Name
        username (str): user username

    Returns:
        bool: return True if Book is found.
    """
    check_user = db.Books.aggregate([
        {'$unwind': f'${input_categories}'},
        {'$unwind': f'${input_categories}.UserDetails'},
        {
            '$match': {
                f'{input_categories}.UserDetails.Username': username,
                f'{input_categories}.Title': input_book_name
            }
        }, {
            '$project': {
                '_id': 0,
                'username': f'${input_categories}.UserDetails.Username'
            }
        }
    ])
    try:
        is_data = list(check_user)
        if is_data and is_data[0]:
            return True
        return False
    except IndexError:
        return False
