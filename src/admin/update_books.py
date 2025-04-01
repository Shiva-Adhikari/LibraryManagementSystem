# local modules
from src.models import Department, Books_
from src.utils import _read_json, _send_response


def update_books(handler):
    data = _read_json(handler)
    category = data.get('category').lower().strip()
    old_book_name = data.get('old_book_name').lower().strip()
    new_book = data.get('new_book')

    department = Department.objects(name=category).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'Department not found'
        }
        _send_response(handler, response, 500)
        return

    # collect ids from department
    book_ids = []
    for book in department.books:
        book_ids.append(book.id)

    try:
        book = Books_.objects.get(title=old_book_name, id__in=book_ids)
    except Exception:
        response = {
            'status': 'error',
            'message': 'Book Not Found to update'
        }
        _send_response(handler, response, 500)
        return

    book.title = new_book['title']
    book.author = new_book['author']
    book.available = new_book['available']

    book.save()
    response = {
        'status': 'success',
        'message': 'Book Updated Successfully'
    }
    _send_response(handler, response, 500)
