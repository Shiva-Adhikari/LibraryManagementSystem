# third party modules
import click

# built in modules
import time

# local modules
from src.utils import verify_jwt_token, find_keys, _delete_books


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

    # call function to delete books
    books = _delete_books(input_category, input_book_name)
    if books:
        click.echo('Successfully Deleted Book')
    else:
        click.echo('Books not Found')
