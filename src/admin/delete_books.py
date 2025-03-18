# local modules
from src.utils import verify_jwt_token, find_keys, _delete_books
from src.utils import _send_response, _read_json


def delete_books(handler):
    """Delete Books from database.
    """

    # check book is empty or not
    check_book = find_keys()
    if not check_book:
        response = {'error': 'Books Not found, Add book first'}
        _send_response(handler, response, 500)
        return

    data = _read_json(handler)
    category = data.get('category').lower().strip()
    book_name = data.get('book_name').lower().strip()

    # verify identity
    verify = verify_jwt_token(handler)
    if not verify:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

    # call function to delete books
    books = _delete_books(category, book_name)
    if books:
        response = {'message': 'Successfully Deleted Book'}
        _send_response(handler, response, 200)
    else:
        response = {'error': 'Book not Found'}
        _send_response(handler, response, 200)
