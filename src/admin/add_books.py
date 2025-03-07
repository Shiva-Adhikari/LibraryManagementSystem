# third party modules
import click

# built in modules
import time

# local modules
from src import logger, verify_jwt_token
from src.models import db


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
def add_books(category, num_books):
    """Add book in database

    Args:
        category (str): Book type like (BCA, BBA, BBS)
        num_books (int): How many books to add in Library.
    """

    categories = {}
    # if list is empty then it create list
    if category not in categories:
        categories[category] = []
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
        auto_id = len(categories[category])
        id = count_books(auto_id, category)
        book_info = {
            'Id': id,
            'Title': book_name,
            'Author': author_name,
            'Available': book_stock
        }
        categories[category].append(book_info)    # append in dictionary
    try:
        verify = verify_jwt_token()
        if not verify:
            click.echo('Data is Discard, please insert again.')
            time.sleep(1)
            return
        insert_doc = db.Books.update_one(
            {category: {'$exists': True}},
            {'$push': {category: {'$each': categories[category]}}},
            upsert=True
        )
        if insert_doc.modified_count > 0 or insert_doc.upserted_id:
            click.echo('Books successfully added')
        else:
            logger.error('Failed to add books')
            click.echo('Failed to add books')
    except Exception as e:
        logger.error(
            f'Failed to save books: {str(e)}',
            exc_info=True)
        click.echo(f'failed to save: {str(e)}')
    time.sleep(1)


def count_books(auto_id, category):
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
