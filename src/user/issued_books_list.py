# local modules
from src.utils import _verify_refresh_token, _send_response
from src.models import UserDetails, Books


@_send_response
def user_issue_books_list(self):
    """display user issued books
    """

    fetch_details, _ = _verify_refresh_token(self, whoami='User')
    if not fetch_details:
        response = {'error': 'Data is Discarded, please login first.'}
        return (response, 401)

    username = fetch_details['username']
    email = fetch_details['email']

    user_detail = UserDetails.objects(username=username, email=email)

    if not user_detail:
        response = {
            'status': 'error',
            'message': 'user not found'
        }
        return (response, 404)

    user_ids = [user.id for user in user_detail]
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
