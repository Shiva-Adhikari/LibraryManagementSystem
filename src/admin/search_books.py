import click
from tabulate import tabulate
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem

table = []


@click.command()
@click.option('--input-book-name', prompt='Enter Book Name', type=str)
def search_books(input_book_name: str) -> None:
    fetch_data = db.Books.find()
    categories = [next(iter(data.keys() - {'_id'})) for data in fetch_data]
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
    header = ['Category', 'Id', 'Title', 'Author', 'Available']
    click.echo(tabulate(table, headers=header, tablefmt='mixed_grid'))
