# third party modules
import click
from tabulate import tabulate
from pymongo import MongoClient

# built in modules
import time

# local modules
from src.admin.stock_book import find_keys
from src.utils import verify_jwt_token


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem

table = []


def search_books() -> None:
    """Search Books from database and display.
    """
    categories = find_keys()
    if not categories:
        click.echo('Books Not found, exiting...')
        time.sleep(2)
        return
    input_book_name = click.prompt('Enter Book Name', type=str).lower()
    verify = verify_jwt_token()
    if not verify:
        time.sleep(1)
        return
    for category in categories:
        fetch_books = db.Books.find(
                    {f"{category}.Title": {
                        "$regex": input_book_name,
                        "$options": "i"}},
                    {category: {"$cond": {
                        "if": {"$isArray": f"${category}"},
                        "then": {"$filter": {
                            "input": f"${category}",
                            "cond": {"$regexMatch": {
                                "input": "$$this.Title",
                                "regex": input_book_name,
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
    display_books()
    input('Press Any Key...')


def display_books() -> None:
    """Display Books in Table view.
    """
    header = ['Category', 'Id', 'Title', 'Author', 'Available']
    click.echo(tabulate(table, headers=header, tablefmt='mixed_grid'))
