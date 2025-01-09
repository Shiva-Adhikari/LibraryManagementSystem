import click
from pymongo import MongoClient
from datetime import datetime


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def process_book(input_categories, input_book_name, set_available, to_date):
    input_categories = input_categories.lower()
    result = db.Books.update_one(
        {f'{input_categories}.Title': input_book_name},
        {
            '$set': {
                f'{input_categories}.$.Available': set_available,
                f'{input_categories}.$.Days': to_date,
                f'{input_categories}.$.Date': datetime.now()
            }
        }
    )
    if result.modified_count > 0:
        print('You got books')


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
@click.option('--to-date', prompt='For how many days you need', type=int)
def _issue_books(input_categories: str, input_book_name: str, to_date: int) -> None:
    process_book(
        input_categories,
        input_book_name,
        0,   # set-available = 0 for issue books
        to_date
        )


def main():
    _issue_books()


if __name__ == '__main__':
    main()

"""Fix issue books also add user email to database when update"""