import click
from pymongo import MongoClient

from config import logging_module
from config import verify_jwt_token


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option(
    '--input-categories',
    prompt=('Enter Book Category'.lower()),
    type=str
)
@click.option(
    '--input-book-name',
    prompt=('Enter Book Name'.lower()),
    type=str
)
def return_books(input_categories: str, input_book_name: str) -> None:
    user_details = verify_jwt_token()
    username = user_details['username']
    email = user_details['email']
    # fetch data or remove data like this code
    # don't use other method to remove this type of nested data.
    result = db.Books.update_one(
        {
            f'{input_categories}.Title': input_book_name,
            f'{input_categories}.UserDetails.Username': username,
            f'{input_categories}.UserDetails.Email': email,
        }, {
            # remove data from nested database
            '$pull': {
                f'{input_categories}.$.UserDetails': {
                    'Username': username,
                    'Email': email
                }
            },
            # increase Available book by 1
            '$inc': {
                f'{input_categories}.$.Available': 1
            }
        }
    )

    if result.modified_count > 0:
        click.echo('You return books')
    else:
        logger.error('Unable to return books')
        click.echo('Unable to return books')
