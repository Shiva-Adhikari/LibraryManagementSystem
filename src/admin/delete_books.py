import click
from pymongo import MongoClient

from config import logging_module


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-category', prompt='Enter book category', type=str)
@click.option('--input-book-name', prompt='Enter book name', type=str)
def delete_books(input_category: str, input_book_name: str) -> None:
    query = {
            f'{input_category}.Title': input_book_name,
            f'{input_category}.$': 1
    }
    search_books = db.Books.find(query)
    if search_books:
        result = db.Books.update_one(
            {f'{input_category}.Title': input_book_name},
            {'$pull': {
                input_category: {'Title': input_book_name}
            }}
        )
        if result.modified_count > 0:
            click.echo('successfully book deleted')
        else:
            logger.error('Unable to delete book')
            click.echo('unable to delete book')
