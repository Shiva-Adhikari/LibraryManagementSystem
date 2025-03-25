# third party modules
from tabulate import tabulate

# local modules
from src.utils import (
    _send_response, _read_json, _verify_refresh_token
)
from src.models import db


books_keys = []


def connect_database():
    """Get list of books

    Returns:
        list: return books in list.
    """

    fetch_books = db.Books.find({}, {'_id': 0})
    for fetch_keys in fetch_books:
        books_keys.append(list(fetch_keys.keys()))

    if books_keys:
        return books_keys


def list_view(handler, category, page_no):
    """Display books in table view.

    Args:
        category (str): book category like (BCA, BBA, BBS)
        page_no (int): page no.

    Returns:
        bool: if user input invalid page then return False or exit.
    """

    # list books from database
    count_books = db.Books.aggregate([
        {'$unwind': f'${category}'},
        {'$count': 'total'}
    ]).next()['total']

    page_size = 5  # Number of elements per page
    total_pages = (count_books + page_size - 1) // page_size

    if page_no < 1 or page_no > total_pages:
        response = {'invalid': f'Invalid page, Available pages up to {total_pages}'}
        _send_response(handler, response, 500)
        return

    skip_line = (page_no - 1) * page_size     # Calculate skip value
    pipeline = [
        {'$match': {category: {'$exists': True}}},
        {'$unwind': f'${category}'},
        {'$skip': skip_line},
        {'$limit': page_size}
    ]

    find_books_page_1 = list(db.Books.aggregate(pipeline))

    table = []
    for extract in find_books_page_1:
        table.append({
            'Id': extract[category]['Id'],
            'Book Name': extract[category]['Title'].capitalize(),
            'Author': extract[category]['Author'].capitalize(),
            'Available': 'Yes' if extract[category]['Available'] else 'No'
        })

    response = {
        'Book List': table,
        'page': f'Page {page_no} of {total_pages}'
    }
    _send_response(handler, response, 200)

    global books_keys
    books_keys = []


def list_books(handler):
    """Display list of Books.
    """

    books_keys = connect_database()
    if not books_keys:
        response = {'error': 'Books Not found, Library is Empty'}
        _send_response(handler, response, 500)
        return

    data = _read_json(handler)
    category = data.get('category').lower()
    page_no = data.get('page')

    user_detail = _verify_refresh_token(handler, whoami='User')
    if not user_detail:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

    list_view(handler, category, page_no)
