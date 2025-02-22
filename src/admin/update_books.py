import time
import click
from pymongo import MongoClient
from config import logging_module
from config import verify_jwt_token

from src.admin.stock_book import find_keys


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def update_books() -> None:
    """Fetch and Update Books from database.
    """
    # check book list is empty or not
    check_book = find_keys()
    if not check_book:
        click.echo('Books Not found, exiting...')
        time.sleep(2)
        return
    # input book
    input_category = click.prompt(
        'Enter book category to search',
        type=str).lower()
    input_book_name = click.prompt(
        'Enter book name to search',
        type=str).lower()
    query = {
        '$and': [
            {input_category: {'$exists': True}},
            {f'{input_category}.Title': input_book_name}
        ]
    }

    search_books = db.Books.find_one(query)
    if search_books:
        click.echo('Book Found Successfully\n')
        book_name = click.prompt('Enter book name to update', type=str)
        book_author = click.prompt(
            'Enter book author name to update',
            type=str
        )
        book_stock = click.prompt('How many books are in stock', type=int)

        verify = verify_jwt_token()
        if not verify:
            click.echo('Data is Discard, please insert again.')
            time.sleep(1)
            return

        update_query = {
            f'{input_category}.Title': input_book_name,
            }, {
                '$set': {
                    f'{input_category}.$.Title': book_name,
                    f'{input_category}.$.Author': book_author,
                    f'{input_category}.$.Available': book_stock
                }
        }
        result = db.Books.update_one(*update_query)

        if result.modified_count > 0:
            click.echo('successfully book updated')
        else:
            logger.error('Unable to update book')
            click.echo('unable to update book')
    else:
        click.echo('Book Not Found')
