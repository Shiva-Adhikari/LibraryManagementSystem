# local modules
from src.utils import _read_get_query, _send_response, route
from src.models import Department, Books


@route('GET', '/api/user/list-books')
@_send_response
@_read_get_query
def list_books(self, data):
    """Display list of Books.
    """

    if not data:
        return
    category = data.get('category').lower()
    page_no = int(data.get('page'))

    department = Department.objects(name=category).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'department not found'
        }
        return (response, 404)

    department_ids = []
    for book in department.books:
        department_ids.append(book.id)

    page_size = 5
    total_books = len(department.books)
    total_pages = (total_books + page_size - 1) // page_size

    if page_no < 1 or page_no > total_pages:
        response = {'invalid': f'Invalid page, Available pages up to {total_pages}'}
        return (response, 404)

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
    return (response, 200)
