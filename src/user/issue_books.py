import click
import json
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta

from config import data_path
from config import logging_module


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


@click.command()
@click.option('--input-categories', prompt=('Enter Book Category'), type=str)
@click.option('--input-book-name', prompt=('Enter Book Name'), type=str)
@click.option('--to-date', prompt='For how many days you need', type=int)
def issue_books(input_categories: str, input_book_name: str, to_date: int,
                set_available=0) -> None:
    try:
        input_categories = input_categories.lower()
        issue_date = datetime.now()
        warning_to_date = to_date - 3
        due_warning = issue_date + timedelta(days=warning_to_date)
        due_date = issue_date + timedelta(days=to_date)
        user_detail = {}
        user_detail = data_path('user')
        with open(user_detail) as file:
            user_detail = json.load(file)
        result = db.Books.update_one(
            {f'{input_categories}.Title': input_book_name},
            {
                '$set': {
                    f'{input_categories}.$.Available': set_available,
                    f'{input_categories}.$.IssueDate': issue_date,
                    f'{input_categories}.$.Days': to_date,
                    f'{input_categories}.$.DueWarning': due_warning,
                    f'{input_categories}.$.DueDate': due_date,
                    f'{input_categories}.$.Details': user_detail
                }
            }
        )
        if result.modified_count > 0:
            click.echo('You got book')
        else:
            logger.error('Unable to get book')
            click.echo('Unable to get book')
    except Exception as e:
        logger.error(f'{str(e)}')
        click.echo(f"got exception as {str(e)}")
