# local modules
from src.models import Department, Books
from src.utils import _send_response, _read_json, route


@route('DELETE', r'^/api/admin/delete-books/(?P<category>[^/]+)$')
@_send_response
@_read_json
def delete_books(self, data):
    """Delete Books from database.
    """

    if not data:
        return

    category = self.Category
    book_name = data.get('book_name', '').lower().strip()

    department = Department.objects(name=category).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'Department not found'
        }
        return (response, 404)

    department_ids = [book.id for book in department.books]

    get_books = Books.objects(title=book_name, id__in=department_ids).first()

    if not get_books:
        response = {
                'status': 'error',
                'message': 'Book not found'
            }
        return (response, 404)

    # delete reference id from department
    department.books.remove(get_books)
    department.save()

    # delete books from collection
    get_books.delete()
    response = {
        'status': 'success',
        'message': 'Successfully Deleted Book'
    }
    return (response, 200)
