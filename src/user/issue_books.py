import click
import json
from pymongo import MongoClient
from datetime import datetime

from config import data_path


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
@click.option('--to-date', prompt='For how many days you need', type=int)
def issue_books(input_categories: str, input_book_name: str, to_date: int,
                set_available=0) -> None:
    input_categories = input_categories.lower()
    user_detail = {}
    user_detail = data_path()
    with open(user_detail) as file:
        user_detail = json.load(file)
    result = db.Books.update_one(
        {f'{input_categories}.Title': input_book_name},
        {
            '$set': {
                f'{input_categories}.$.Available': set_available,
                f'{input_categories}.$.Days': to_date,
                f'{input_categories}.$.Date': datetime.now(),
                f'{input_categories}.$.Details': user_detail
            }
        }
    )
    if result.modified_count > 0:
        click.echo('You got book')
    else:
        """ ADD LOGGING MODULE """
        click.echo('Unable to get book')
