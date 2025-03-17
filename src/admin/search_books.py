# third party modules
from tabulate import tabulate

# local modules
from src.utils import verify_jwt_token, find_keys, _send_response, _read_json
from src.models import db


def search_books(handler):
    """Search Books from database and display.
    """

    categories = find_keys()
    if not categories:
        response = {'error': 'Books is Empty, add books first'}
        _send_response(handler, response, 500)
        return

    data = _read_json(handler)
    book_name = data.get('book_name')

    # verify = verify_jwt_token()
    # if not verify:
        # return

    table = []

    for category in categories:
        fetch_books = db.Books.find(
                    {f"{category}.Title": {
                        "$regex": book_name,
                        "$options": "i"}},
                    {category: {"$cond": {
                        "if": {"$isArray": f"${category}"},
                        "then": {"$filter": {
                            "input": f"${category}",
                            "cond": {"$regexMatch": {
                                "input": "$$this.Title",
                                "regex": book_name,
                                "options": "i"
                            }}
                        }},
                        "else": f"${category}"
                    }}}
                )
        for extract in fetch_books:
            keys = next(iter(extract.keys() - {'_id'}))
            for book in extract[keys]:
                table.append([
                    keys.capitalize(),
                    book['Id'],
                    book['Title'].capitalize(),
                    book['Author'].capitalize(),
                    'Yes' if book['Available'] else 'No'
                ])
    display_books(handler, table)


def display_books(handler, table) -> None:
    """Display Books in Table view.
    """

    header = ['Category', 'Id', 'Title', 'Author', 'Available']
    _table = (tabulate(table, headers=header, tablefmt='grid'))
    response = {'books': _table}
    _send_response(handler, response, 200)
