import click
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient

from config import logging_module
from config import verify_jwt_token


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
@click.option('--to-date', prompt='For how many days you need', type=int)
def issue_books(input_categories: str, input_book_name: str, to_date: int,
                ) -> None:
    try:
        input_categories = input_categories.lower()
        issue_date = datetime.now()
        warning_to_date = to_date - 3
        due_warning = issue_date + timedelta(days=warning_to_date)
        due_date = issue_date + timedelta(days=to_date)
        user_detail = verify_jwt_token()
        username = user_detail['username']
        email = user_detail['email']
        # validata_user(input_categories, input_book_name, username)
        # input('hold')
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


"""
def validata_user(input_categories, input_book_name, username):
    check_user = db.Books.find(
        {
            f'{input_categories}.Title': input_book_name,
            f'{input_categories}.UserDetails.Username': username,
            # f'{input_categories}.UserDetails.$.Username': True, '_id': 0
        },
        {
            # f'{input_categories}.UserDetails.Username$': True,
            f'{input_categories}.UserDetails.$': 1,
            '_id': 0
        }
    )
# check_user = db.Books.aggregate([
#     {
#         '$match': {
#             f'{input_categories}.Title': input_book_name,
#             f'{input_categories}.UserDetails.Username': username
#         }
#     },
#     {
#         '$project': {
#             '_id': 0,
#             'bca': {
#                 '$filter': {
#                     'input': f'${input_categories}',
#                     'as': 'book',
#                     'cond': {'$eq': ['$$book.Title', input_book_name]}
#                 }
#             }
#         }
#     }
# ])
    print(f'check_user: {list(check_user)}')
    if check_user:
        print('yes')
    else:
        print('no')
    exit()
"""
