# local modules
from src.utils import (
    logger, find_keys, verify_jwt_token,
    _find_books, _update_books
)
from src.models import BookCategories
from src.utils import _read_json, _send_response


def update_books(handler):
    """Fetch and Update Books from database.
    """

    # check book list is empty or not
    check_book = find_keys()
    if not check_book:
        response = {'error': 'Book Not found, Add books first'}
        _send_response(handler, response, 500)
        return

    data = _read_json(handler)
    category = data.get('category').lower().strip()
    old_book_name = data.get('old_book_name').lower().strip()
    new_book = data.get('new_book')

    search_books = _find_books(category, old_book_name)
    if search_books:
        book_info = {}

        book_info = {
            'Title': new_book.get('title').lower().strip(),
            'Author': new_book.get('author').lower().strip(),
            'Available': new_book.get('available')
        }

        verify = verify_jwt_token(handler)
        if not verify:
            response = {'error': 'Data is Discarded, please login first.'}
            _send_response(handler, response, 500)
            return

        # Mongo Model
        book = BookCategories(
            Title=book_info['Title'],
            Author=book_info['Author'],
            Available=book_info['Available']
        )

        res = _update_books(category, old_book_name, book)
        if res:
            response = {'message': 'Updated Books Successfully'}
            _send_response(handler, response, 200)
        else:
            response = {'error': 'Failed to Update'}
            _send_response(handler, response, 500)
            logger.debug('Failed to Update')

    else:
        response = {'error': 'Old Book Not Found'}
        _send_response(handler, response, 500)
