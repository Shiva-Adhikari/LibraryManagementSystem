# local modules
from src.models import Department, Books
from src.utils import _read_json, _send_response, route


@route('PUT', r'^/api/admin/update-books/(?P<category>[^/]+)$')
@_send_response
@_read_json
def update_books(self, data):
    if not data:
        return

    category = self.Category
    old_book_name = data.get('old_book_name').lower().strip()
    new_book = data.get('new_book')

    department = Department.objects(name=category).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'Department not found'
        }
        return (response, 404)

    # collect ids from department
    book_ids = []
    for book in department.books:
        book_ids.append(book.id)

    new_book_title = new_book['title']
    # check book exists or not before update
    search_book = Books.objects(title=new_book_title, id__in=book_ids).first()
    if search_book:
        response = {
            'status': 'error',
            'message': 'Book already present'
        }
        return (response, 409)

    try:
        book = Books.objects.get(title=old_book_name, id__in=book_ids)
    except Exception:
        response = {
            'status': 'error',
            'message': 'Book Not Found to update'
        }
        return (response, 404)

    book.title = new_book['title']
    book.author = new_book['author']
    book.available = new_book['available']

    book.save()
    response = {
        'status': 'success',
        'message': 'Book Updated Successfully'
    }
    return (response, 200)
