# built in modules
from datetime import datetime, timedelta

# local modules
from src.utils import (
    _send_response, _read_json, _verify_refresh_token
)


def issue_books(handler):
    from src.models import Books_, UserDetails, Department
    """User issue book.
    """

    data = _read_json(handler)
    if not data:
        return

    category_name = data.get('category').lower().strip()
    book_name = data.get('book_name').lower().strip()
    to_date = data.get('days')

    if not isinstance(to_date, int):
        response = {
            'status': 'error',
            'message': 'enter days not string'
        }
        return _send_response(handler, response, 500)

    issue_date = datetime.now()
    warning_to_date = to_date - 3
    due_warning = issue_date + timedelta(days=warning_to_date)
    due_date = issue_date + timedelta(days=to_date)

    user_detail = _verify_refresh_token(handler, whoami='User')
    if not user_detail:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

    username = user_detail['username']
    email = user_detail['email']

    department = Department.objects(name=category_name).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'department not found'
        }
        return _send_response(handler, response, 500)

    department_ids = []
    for book in department.books:
        department_ids.append(book.id)

    books = Books_.objects(title=book_name, id__in=department_ids).first()

    if not books:
        response = {
            'status': 'error',
            'message': 'book not found'
        }
        return _send_response(handler, response, 500)

    book_info = {
        'username': username.lower(),
        'email': email.lower(),
        'days': to_date,
        'issue_date': issue_date,
        'due_warning': due_warning,
        'due_date': due_date
    }
    user_details = UserDetails(**book_info)
    user_details.save()
    books.user_details.append(user_details.id)
    books.save()
    response = {
        'status': 'success',
        'message': 'Successfully issued book'
    }
    return _send_response(handler, response, 200)
