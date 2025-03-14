# third party modules
import click

# built in modules
import time

# local modules
from src.utils import (
    logger, find_keys, verify_jwt_token,
    _find_books, _update_books
)
from src.models import BookCategories


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
        'Enter book category to search', type=str).lower()
    input_book_name = click.prompt(
        'Enter book name to search', type=str).lower()

    search_books = _find_books(input_category, input_book_name)
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

        # Mongo Model
        new_book: BookCategories = BookCategories(
            Title=book_name,
            Author=book_author,
            Available=book_stock
        )

        res = _update_books(input_category, input_book_name, new_book)
        if res:
            print('Updated Books Successfully')
        else:
            print('Failed to Update')
            logger.debug('Failed to Update')

    else:
        click.echo('Book Not Found')
