# local modules
from src.utils import _send_response, _read_json, _verify_refresh_token
from src.models import Department, Books, UserDetails


@_send_response
@_read_json
def return_books(self, data):
    """return books which is already issued by user

    Returns:
        bool: if issued books not available, exit.
    """

    # data = _read_json(handler)
    if not data:
        return

    category_name = data.get('category').lower().strip()
    book_name = data.get('book_name').lower().strip()

    user_details = _verify_refresh_token(self, whoami='User')
    if not user_details:
        response = {'error': 'Data is Discarded, please login first.'}
        return (response, 401)

    if isinstance(user_details.get('token'), dict):
        username = user_details['token']['payload']['username']
        email = user_details['token']['payload']['email']
    else:
        username = user_details['username']
        email = user_details['email']

    department = Department.objects(name=category_name).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'department not found'
        }
        return (response, 404)

    department_ids = []
    for book in department.books:
        department_ids.append(book.id)

    book = Books.objects(title=book_name, id__in=department_ids).first()
    if not book:
        response = {
            'status': 'error',
            'message': 'book not found'
        }
        return (response, 404)

    books_ids = [book.id for book in book.user_details]
    user_detail = UserDetails.objects(
        username=username, email=email, id__in=books_ids).first()
    if not user_detail:
        response = {
            'status': 'error',
            'message': 'book not found, issue book first'
        }
        return (response, 404)

    book.user_details.remove(user_detail)
    book.available = book.available + 1
    book.save()

    user_detail.delete()

    response = {
        'status': 'success',
        'message': 'successfully returned book'
    }
    return (response, 200)
