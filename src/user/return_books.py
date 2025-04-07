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

    username = user_details['username']
    email = user_details['email']

    department = Department.objects(name=category_name).first()
    print(f"Department: {department}")
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
    print(f"book: {book}")
    if not book:
        response = {
            'status': 'error',
            'message': 'book not found'
        }
        return (response, 404)

    user_detail = UserDetails.objects(username=username, email=email).first()
    print(f"user_detail: {user_detail}")
    if not user_detail:
        response = {
            'status': 'error',
            'message': 'user not found'
        }
        return (response, 404)

    if user_detail.id in [user.id for user in book.user_details]:
        book.user_details.remove(user_detail)
        book.available = book.available + 1
        book.save()

        user_detail.delete()

        response = {
            'status': 'success',
            'message': 'successfully returned book'
        }
        return (response, 200)

    response = {
        'status': 'error',
        'message': 'Book not found'
    }
    return (response, 404)
