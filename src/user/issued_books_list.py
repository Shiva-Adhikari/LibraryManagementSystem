# local modules
from src.utils import _verify_refresh_token, _send_response, route
from src.models import UserDetails, Books


@route('GET', '/api/user/issued_books_list')
@_send_response
def user_issue_books_list(self):
    """display user issued books
    """

    user_detail = _verify_refresh_token(self, whoami='User')
    if not user_detail:
        response = {'error': 'Data is Discarded, please login first.'}
        return (response, 401)

    if isinstance(user_detail.get('token'), dict):
        username = user_detail['token']['payload']['username']
        email = user_detail['token']['payload']['email']
    else:
        username = user_detail['username']
        email = user_detail['email']

    user_details = UserDetails.objects(username=username, email=email)
    if not user_details:
        response = {
            'status': 'error',
            'message': 'user not found'
        }
        return (response, 404)

    user_ids = [user.id for user in user_details]
    books = Books.objects(user_details__in=user_ids)
    if not books:
        response = {
            'status': 'error',
            'message': 'issue book first'
        }
        return (response, 404)

    # gather issued books using list comprehension
    books_list = [
        {
            'title': book.title,
            'author': book.author,
        } for book in books
    ]

    response = {
        'status': 'success',
        'message': books_list
    }
    return (response, 200)
