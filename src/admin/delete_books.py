import time
import click
from pymongo import MongoClient

from config import logging_module
from src.admin.stock_book import find_keys


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def delete_books() -> None:
    """check book is empty or not"""
    check_book = find_keys()
    if not check_book:
        click.echo('Books Not found, exiting...')
        time.sleep(2)
        return
    """input books"""
    input_category = click.prompt('Enter book category', type=str).lower()
    input_book_name = click.prompt('Enter book name', type=str).lower()
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
