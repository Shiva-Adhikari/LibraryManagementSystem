import click
# import logging
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-category', prompt='Enter book category', type=str)
@click.option('--input-book-name', prompt='Enter book name', type=str)
def delete_books(input_category: str, input_book_name: str) -> None:
    query = {
        '$and': [
            {input_category: {'$exists': True}},
            {f'{input_category}.Title': input_book_name}
        ]
    }
    search_books = db.Books.find(query)
    if search_books:
        result = db.Books.delete_one(query)
        if result.deleted_count > 0:
            print('successfully book deleted')
        else:
            print('unable to delete book')


if __name__ == '__main__':
    delete_books()
