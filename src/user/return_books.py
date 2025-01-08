import click
from pymongo import MongoClient
from issue_books import process_book


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
def _return_books(input_categories: str, input_book_name: str) -> None:
    process_book(
        input_categories,
        input_book_name,
        1   # set-available = 0 for issue books
        )


def main():
    _return_books()


if __name__ == '__main__':
    main()
