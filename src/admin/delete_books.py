# local modules
from src.models import Department, Books_
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

    book_to_delete = Books_.objects.get(title=book_name)

    if not book_to_delete:
        response = {
                'status': 'error',
                'message': 'Book not found'
            }
        return _send_response(handler, response, 500)

    # department ko ra, book ko id match vayo vani
    if book_to_delete.id in [book.id for book in department.books]:
        # delete reference id from department
        department.books.remove(book_to_delete)
        department.save()

        # delete books from collection
        book_to_delete.delete()

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
