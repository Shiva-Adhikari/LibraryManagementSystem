# local modules
from src.utils import _send_response, _read_json, _verify_refresh_token
from src.models import Department, Books, UserDetails


'''
def user_issue_books_list(handler):
    """display user issued books

    Returns:
        bool: if user issued books found then it return True.
    """

    # user_details = verify_jwt_token(handler)
    user_details = _verify_refresh_token(handler, whoami='User')
    if not user_details:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

    username = user_details['username']
    email = user_details['email']
    category_check_merge = []
    category_key = find_keys()

    for category in category_key:
        check_book = db.Books.aggregate([
                {'$unwind': f'${category}'},
                {'$unwind': f'${category}.UserDetails'},
                {'$match': {f'{category}.UserDetails.Username': username}}
        ])
        category_check_merge.append(list(check_book))

    # if all get false, then exit
    if all(not check_detail for check_detail in category_check_merge):
        return False

    fetch_issue_books = []
    for category_keys in category_key:
        result = db.Books.aggregate([
            {'$unwind': f'${category_keys}'},
            {'$unwind': f'${category_keys}.UserDetails'},
            {
                '$match': {
                    f'{category_keys}.UserDetails.Username': username,
                    f'{category_keys}.UserDetails.Email': email
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'Id': f'${category_keys}.Id',
                    'Title': f'${category_keys}.Title',
                    'Author': f'${category_keys}.Author',
                }
            }
        ])

        for book in result:
            fetch_issue_books.append({
                'Category': category_keys,
                'Id': book['Id'],
                'Title': book['Title'],
                'Author': book['Author']
            })

    if fetch_issue_books:
        return True


def return_books(handler) -> None:
    """return books which is already issued by user

    Returns:
        bool: if issued books not available, exit.
    """

    is_books_empty = user_issue_books_list(handler)
    if not is_books_empty:
        response = {'error': 'Your Issue list is empty. First Issue Book'}
        _send_response(handler, response, 500)
        return

    data = _read_json(handler)
    category = data.get('category').lower().strip()
    book_id = data.get('book_id')

    user_details = _verify_refresh_token(handler, whoami='User')
    if not user_details:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

    username = user_details['username']
    email = user_details['email']
    # fetch data or remove data like this code
    # don't use other method to remove this type of nested data.
    result = db.Books.update_one(
        {
            f'{category}.Id': book_id,
            f'{category}.UserDetails.Username': username,
            f'{category}.UserDetails.Email': email,
        }, {
            # remove data from nested database
            '$pull': {
                # [elem] is used to find that particular user detail
                f'{category}.$[elem].UserDetails': {
                    'Username': username,
                    'Email': email
                }
            },
            # increase Available book by 1
            '$inc': {
                f'{category}.$[elem].Available': 1
            }
        },
        # and we need this arrary_filter when using [elem]
        array_filters=[
            {f'elem.Id': book_id}
        ]
    )

    if result.modified_count > 0:
        response = {'message': 'You Successfully return books'}
        _send_response(handler, response, 200)
    else:
        response = {'error': 'Unable to return books, Books not found.'}
        _send_response(handler, response, 500)
'''


def return_books(handler):
    """return books which is already issued by user

    Returns:
        bool: if issued books not available, exit.
    """

    data = _read_json(handler)
    if not data:
        return

    category_name = data.get('category').lower().strip()
    book_name = data.get('book_name').lower().strip()

    user_details = _verify_refresh_token(handler, whoami='User')
    if not user_details:
        response = {'error': 'Data is Discarded, please login first.'}
        return _send_response(handler, response, 401)

    username = user_details['username']
    email = user_details['email']

    department = Department.objects(name=category_name).first()
    if not department:
        response = {
            'status': 'error',
            'message': 'department not found'
        }
        return _send_response(handler, response, 404)

    department_ids = []
    for book in department.books:
        department_ids.append(book.id)

    book = Books.objects(title=book_name, id__in=department_ids).first()
    if not book:
        response = {
            'status': 'error',
            'message': 'book not found'
        }
        return _send_response(handler, response, 404)

    user_detail = UserDetails.objects(username=username, email=email).first()
    if not user_detail:
        response = {
            'status': 'error',
            'message': 'user not found'
        }
        return _send_response(handler, response, 404)

    if user_detail.id in [user.id for user in book.user_details]:
        book.user_details.remove(user_detail)
        book.available = book.available + 1
        book.save()

        user_detail.delete()

        response = {
            'status': 'success',
            'message': 'successfully returned book'
        }
        return _send_response(handler, response, 200)

    response = {
        'status': 'error',
        'message': 'Book not found'
    }
    return _send_response(handler, response, 404)
