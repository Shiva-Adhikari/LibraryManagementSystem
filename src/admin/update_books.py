import click
# import logging
from pymongo import MongoClient


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
        update_query = {
            f'{input_category}.Title': input_book_name,
            }, {
                '$set': {
                    f'{input_category}.$.Title': book_name,
                    f'{input_category}.$.Author': book_author
                }
        }
        result = db.Books.update_one(*update_query)
        if result.modified_count > 0:
            print('successfully book updated')
        else:
            # ADD LOGGING HERE
            print('unable to update book')
    else:
        click.echo('Book Not Found')


if __name__ == '__main__':
    update_books()
