# built in modules
from datetime import datetime, timedelta

# local modules
from src.utils import (
    logger, find_keys, validate_user,
    _send_response, _read_json, _verify_refresh_token
)
from src.models import db


def issue_books(handler) -> None:
    """User issue book.
    """

    # check if books is empty or not
    check_books = find_keys()
    if not check_books:
        response = {'error': 'Books Not found, Library is Empty'}
        _send_response(handler, response, 500)
        return

    data = _read_json(handler)
    category = data.get('category').lower().strip()
    book_name = data.get('book_name').lower().strip()
    to_date = data.get('days')

    try:
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

        # call validate_user from utils_
        does_exist = validate_user(category, book_name, username)
        if does_exist:
            response = {'error': 'Book already Issued, unable to issue again'}
            _send_response(handler, response, 500)
            return

        # Ensure book is available before issuing
        book_info = db.Books.find_one(
            {f'{category}.Title': book_name, f'{category}.Available': {"$gt": 0}},
            {f'{category}.$': 1}
        )
        if not book_info:
            response = {'error': 'Book not available or not found'}
            _send_response(handler, response, 500)
            return

        result = db.Books.update_one(
            {f'{category}.Title': book_name},
            {
                '$inc': {
                    f'{category}.$.Available': -1
                },

                '$push': {
                    f'{category}.$.UserDetails':
                        {
                            'Username': username,
                            'Email': email,
                            'Days': to_date,
                            'IssueDate': issue_date,
                            'DueWarning': due_warning,
                            'DueDate': due_date,
                        }

                }
            }
        )

        if result.modified_count > 0:
            response = {'message': 'You got book.'}
            _send_response(handler, response, 200)
        else:
            response = {'error': 'Unable to get book, Try Again.'}
            _send_response(handler, response, 500)

    except Exception as e:
        logger.error(e)
        response = {'exception': f'Unable to get book, Try Again. as {str(e)}'}
        _send_response(handler, response, 500)
