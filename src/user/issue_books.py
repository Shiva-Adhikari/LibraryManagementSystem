import click
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def process_book(input_categories, input_book_name, set_available):
    input_categories = input_categories.lower()
    result = db.Books.update_one(
        {f'{input_categories}.Title': input_book_name},
        {'$set': {f'{input_categories}.$.Available': set_available}}
    )
    if result.modified_count > 0:
        print('You got books')
    else:
        print('Book not found')


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
def _issue_books(input_categories: str, input_book_name: str) -> None:
    process_book(
        input_categories,
        input_book_name,
        0   # set-available = 0 for issue books
        )


def main():
    _issue_books()


if __name__ == '__main__':
    main()
