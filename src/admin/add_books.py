# local modules
from src.utils import (
    logger, _insert_books, count_books,
    _read_json, _send_response, _verify_refresh_token
)
from src.models import BookCategories


def add_books(handler):
    """Add book in database

    Args:
        category (str): Book type like (BCA, BBA, BBS)
        num_books (int): How many books to add in Library.
    """

    data = _read_json(handler)

    # categories: dict[int | str, list[int | str]] = {}
    categories = {}
    category = ''
    no_books = []

    # count books
    auto_id = 0

    for category, categories in data.items():
        for books in categories:
            auto_id = len(no_books)
            # call count_books function from utils_
            id = count_books(auto_id, category)

            book_info = {
                'Id': id,
                'Title': books['Title'].lower(),
                'Author': books['Author'].lower(),
                'Available': books['Available']
            }

            # check in model
            n_books = BookCategories(
                Id=book_info['Id'],
                Title=book_info['Title'],
                Author=book_info['Author'],
                Available=book_info['Available'],
            ).to_mongo()
            no_books.append(n_books)    # append in dictionary

    try:
        verify = _verify_refresh_token(handler, whoami='Admin')
        if not verify:
            response = {'message': 'Data is Discarded, please login first.'}
            _send_response(handler, response, 500)
            return

        # call function from utils/mongo
        check_book = _insert_books(category, no_books)
        if check_book:
            response = {'message': 'Books successfully added'}
            _send_response(handler, response, 200)
        else:
            logger.debug('Failed to add books')
            response = {'error': 'Failed to add books'}
            _send_response(handler, response, 500)
    except Exception as e:
        logger.error(
            f'Failed to save books: {str(e)}',
            exc_info=True)
        response = {'exception': 'Failed to add books'}
        _send_response(handler, response, 500)
