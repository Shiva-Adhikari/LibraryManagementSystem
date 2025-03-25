# local modules
from src.utils import (
    find_keys, _send_response, _read_json,
    _verify_refresh_token
)
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
    book_name = data.get('book_name').lower().strip()

    verify = _verify_refresh_token(handler, whoami='Admin')
    if not verify:
        response = {'error': 'Data is Discarded, please login first.'}
        _send_response(handler, response, 500)
        return

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
                table.append({
                    'Category': keys.capitalize(),
                    'Id': book['Id'],
                    'Book Name': book['Title'].capitalize(),
                    'Author': book['Author'].capitalize(),
                    'Available': 'Yes' if book['Available'] else 'No'
                })

    response = {
        'Book List': table
    }
    _send_response(handler, response, 200)
