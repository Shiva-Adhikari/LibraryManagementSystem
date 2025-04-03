# local modules
from src.models import Department, Books
from src.utils import _send_response, _read_json


def delete_books(handler):
    """Delete Books from database.
    """

    data = _read_json(handler)
    category = data.get('category', '').lower().strip()
    book_name = data.get('book_name', '').lower().strip()

    department = Department.objects(name=category).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'Department not found'
        }
        return _send_response(handler, response, 500)

    get_books = Books.objects.get(title=book_name)

    if not get_books:
        response = {
                'status': 'error',
                'message': 'Book not found'
            }
        return _send_response(handler, response, 500)

    # department ko ra, book ko id match vayo vani
    if get_books.id in [book.id for book in department.books]:
        # delete reference id from department
        department.books.remove(get_books)
        department.save()

        # delete books from collection
        get_books.delete()

        response = {
            'status': 'success',
            'message': 'Successfully Deleted Book'
        }
        return _send_response(handler, response, 200)

    response = {
                'status': 'error',
                'message': 'Book not found in this department'
            }
    return _send_response(handler, response, 500)
