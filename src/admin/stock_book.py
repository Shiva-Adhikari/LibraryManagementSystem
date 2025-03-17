# third party modules
from tabulate import tabulate

# local modules
from src.utils import verify_jwt_token, find_keys, _send_response
from src.models import db


def stock_book(handler):
    """Search less than 5 Books and display.
    """

    # verify = verify_jwt_token()
    # if not verify:
        # return

    category_key = find_keys()
    if not category_key:
        # click.echo('Books Not found, exiting...')
        # time.sleep(2)
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
        table.append([
            result['Category'].capitalize(),
            result['Title'].capitalize(),
            result['Available']
        ])
    header = ['Category', 'Title', 'Available']
    _table = (tabulate(table, headers=header, tablefmt='grid'))
    response = {'books': _table}
    _send_response(handler, response, 200)
