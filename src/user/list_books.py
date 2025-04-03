# local modules
from src.utils import _read_json, _send_response
from src.models import Department, Books


def list_books(handler):
    """Display list of Books.
    """

    data = _read_json(handler)
    if not data:
        return
    category = data.get('category').lower()
    page_no = data.get('page')

    department = Department.objects(name=category).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'department not found'
        }
        return _send_response(handler, response, 500)

    department_ids = []
    for book in department.books:
        department_ids.append(book.id)

    page_size = 5
    total_books = len(department.books)
    total_pages = (total_books + page_size - 1) // page_size

    if page_no < 1 or page_no > total_pages:
        response = {'invalid': f'Invalid page, Available pages up to {total_pages}'}
        _send_response(handler, response, 500)
        return

    skip_line = (page_no - 1) * page_size

    books = Books.objects(id__in=department_ids).skip(skip_line).limit(page_size)

    # convert to readable JSON-like format
    books_list = [book.to_mongo().to_dict() for book in books]

    list_books = [
        {
            'category': category,
            'title': book['title'],
            'author': book['author'],
            'available': book['available'],
        }
        for book in books_list
    ]

    response = {
        'status': 'success',
        'message': list_books
    }
    return _send_response(handler, response, 200)
