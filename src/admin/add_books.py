from typing import List
from pymongo import MongoClient
import click
import logging


categories = {}

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option(
    '--category',
    prompt=(
        'What Type of book you want to ADD in Library'
        ).lower(),
    type=str)
@click.option(
    '--num_books',
    prompt=(
        'How Many books you want to add in Library'
        ).lower(),
    type=click.IntRange(min=1),
    default=1)
def write_books(category, num_books):
    """ Write books in files """
    global categories
    # if list is empty then it create list
    if category not in categories:
        categories[category]: List = []
    for i in range(num_books):
        book_name = click.prompt(
            f'\nEnter "{category}" Book Name {i+1} '
            ).lower()
        author_name = click.prompt(f'Enter "{category}" Author name').lower()
        book_info = {
            'Id': len(categories[category]) + 1,
            'Title': book_name,
            'Author': author_name,
            'Available': 1
        }
        categories[category].append(book_info)    # append in dictionary
    try:
        """it push double list in database"""
        insert_doc = db.Books.update_one(
            {category: {'$exists': True}},
            {'$push': {category: {'$each': categories[category]}}},
            upsert=True
        )
        if insert_doc.modified_count > 0 or insert_doc.upserted_id:
            click.echo('Books successfully added')
        else:
            click.echo('Failed to add books')
    except Exception as e:
        logging.error(
            f'Failed to save (add_books): {str(e)}',
            exc_info=True)
        click.echo(f'failed to save: {str(e)}')
    input("Press Any Key...")


"""DO ID AUTO MANAGE"""
"""convert password to hash"""
if __name__ == '__main__':
    write_books()
