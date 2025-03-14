# third party modules
import click

# built in modules
import time

# local modules
from src.utils import logger, _insert_books, verify_jwt_token
from src.models import db, BookCategories


start_id = 0


@click.command()
@click.option(
    '--category',
    prompt=(
        'What Type of book you want to ADD in Library'
        ).lower(),
    type=str)
@click.option(
    '--num_books',
    prompt=(
        'How Many books you want to add in Library'
        ).lower(),
    type=click.IntRange(min=1),
    default=1)
def add_books(category: str, num_books: int):
    """Add book in database

    Args:
        category (str): Book type like (BCA, BBA, BBS)
        num_books (int): How many books to add in Library.
    """

    categories: dict[int | str, list[int | str]] = {}
    # if list is empty then it create list
    if category not in categories:
        no_books: list[int | str] = []
    for i in range(num_books):
        book_name = click.prompt(
            f'\nEnter "{category}" Book Name ({i+1}) '
            ).lower()
        author_name = click.prompt(
            f'Enter "{category}" Author name',
            type=str).lower()
        book_stock = click.prompt(
            f'How many stock are there {category}',
            type=int)

        # count books
        auto_id = len(no_books)

        # get id
        id = count_books(auto_id, category)
        book_info = {
            'Id': id,
            'Title': book_name,
            'Author': author_name,
            'Available': book_stock
        }

        # check in model
        n_books: BookCategories = BookCategories(
            Id=book_info['Id'],
            Title=book_info['Title'],
            Author=book_info['Author'],
            Available=book_info['Available'],
        ).to_mongo()
        no_books.append(n_books)    # append in dictionary

    try:
        verify = verify_jwt_token()
        if not verify:
            click.echo('Data is Discard, please insert again.')
            time.sleep(1)
            return

        # call function from utils/mongo
        check_book = _insert_books(category, no_books)
        if check_book:
            click.echo('Books successfully added')
        else:
            logger.debug('Failed to add books')
            click.echo('Failed to add books')
    except Exception as e:
        logger.error(
            f'Failed to save books: {str(e)}',
            exc_info=True)
        click.echo(f'failed to save: {str(e)}')
    time.sleep(1)


def count_books(auto_id: int, category: str):
    """Get book id

    Args:
        auto_id (int): count list of books
        category (str): Book Name

    Returns:
        int: return Number of Books
    """

    global start_id
    try:
        count_book = db.Books.aggregate([
            {
                '$match': {category: {'$exists': True}}
            },
            {
                '$project': {
                    '_id': 0,
                    'count': {
                        '$add': [
                            {'$size': f'${category}'},
                            1
                        ]
                    }
                }
            }
        ]).next()['count']
        if start_id == 0:
            start_id = count_book
        else:
            start_id += 1
        return start_id
    except StopIteration:
        return auto_id + 1
