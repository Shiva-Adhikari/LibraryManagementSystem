# third party modules
import click

# built in modules
import time

# local modules
from src import logger, verify_jwt_token
from src.admin.stock_book import find_keys
from src.models.settings import db


# client = MongoClient('localhost', 27017)
# db = client.LibraryManagementSystem


def delete_books() -> None:
    """Delete Books from database.
    """

    # check book is empty or not
    check_book = find_keys()
    if not check_book:
        click.echo('Books Not found, exiting...')
        time.sleep(2)
        return
    # input books
    input_category = click.prompt('Enter book category', type=str).lower()
    input_book_name = click.prompt('Enter book name', type=str).lower()
    # verify identity
    verify = verify_jwt_token()
    if not verify:
        click.echo('Data is Discard, please insert again.')
        time.sleep(1)
        return
    query = {
            f'{input_category}.Title': input_book_name,
            f'{input_category}.$': 1
    }
    search_books = db.Books.find(query)
    if search_books:
        result = db.Books.update_one(
            {f'{input_category}.Title': input_book_name},
            {'$pull': {
                input_category: {'Title': input_book_name}
            }}
        )
        if result.modified_count > 0:
            click.echo('successfully book deleted')
        else:
            logger.error('Unable to delete book')
            click.echo('unable to delete book')
