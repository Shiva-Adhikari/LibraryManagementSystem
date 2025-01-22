import click
from pymongo import MongoClient
from config import logging_module


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option(
    '--input-category',
    prompt='Enter book category to search',
    type=str
)
@click.option(
    '--input-book-name',
    prompt='Enter book name to search',
    type=str
)
def update_books(input_category: str, input_book_name: str) -> None:
    query = {
        '$and': [
            {input_category: {'$exists': True}},
            {f'{input_category}.Title': input_book_name}
        ]
    }
    search_books = db.Books.find_one(query)
    if search_books:
        click.echo('Book Found Successfully\n')
        book_name = click.prompt('Enter book name to update', type=str)
        book_author = click.prompt(
            'Enter book author name to update',
            type=str
        )
        book_stock = click.prompt('How many books are in stock', type=int)
        update_query = {
            f'{input_category}.Title': input_book_name,
            }, {
                '$set': {
                    f'{input_category}.$.Title': book_name,
                    f'{input_category}.$.Author': book_author,
                    f'{input_category}.$.Available': book_stock
                }
        }
        result = db.Books.update_one(*update_query)
        if result.modified_count > 0:
            click.echo('successfully book updated')
        else:
            logger.error('Unable to update book')
            click.echo('unable to update book')
    else:
        click.echo('Book Not Found')
