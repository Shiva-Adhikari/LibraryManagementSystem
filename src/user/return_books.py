import click
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
def return_books(input_categories: str, input_book_name: str, set_available=1
                 ) -> None:
    input_categories = input_categories.lower()
    result = db.Books.update_one(
        {f'{input_categories}.Title': input_book_name},
        {
            '$set': {
                f'{input_categories}.$.Available': set_available
            },
            '$unset': {
                f'{input_categories}.$.IssueDate': '',
                f'{input_categories}.$.Days': '',
                f'{input_categories}.$.DueWarning': '',
                f'{input_categories}.$.DueDate': '',
                f'{input_categories}.$.Details': ''
            }
        },
        upsert=False
    )
    if result.modified_count > 0:
        click.echo('You return books')
    else:
        """ ADD LOGGING MODULE """
        click.echo('Unable to return books')
