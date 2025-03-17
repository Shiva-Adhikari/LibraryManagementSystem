# local modules
from src.utils import logger, _insert_books, verify_jwt_token
from src.models import db, BookCategories
from src.utils import _read_json, _send_response


start_id = 0


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
        # verify = verify_jwt_token()
        # if not verify:
            # click.echo('Data is Discarded, please login first.')
            # return

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
