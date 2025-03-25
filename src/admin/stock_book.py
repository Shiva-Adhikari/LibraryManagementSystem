# local modules
from src.utils import find_keys, _send_response, _verify_refresh_token
from src.models import db


def stock_book(handler):
    """Search less than 5 Books and display.
    """

    verify = _verify_refresh_token(handler, whoami='Admin')
    if not verify:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

    category_key = find_keys()
    if not category_key:
        response = {'error': 'Books Not found, Add book first'}
        _send_response(handler, response, 500)
        return

    append_result = []
    for category in category_key:
        results = db.Books.aggregate([
            {'$unwind': f'${category}'},
            {
                '$match': {
                    f'{category}.Available': {'$lt': 5}
                }
            }, {
                '$project': {
                    'Title': f'${category}.Title',
                    'Available': f'${category}.Available',
                    '_id': 0
                }
            }
        ])
        for result in results:
            append_result.append({
                'Category': category,
                'Title': result['Title'],
                'Available': result['Available'],
            })
    table = []
    for result in append_result:
        table.append({
            'Category': result['Category'].capitalize(),
            'Title': result['Title'].capitalize(),
            'Available': result['Available']
        })

    response = {'Books List': table}
    _send_response(handler, response, 200)
