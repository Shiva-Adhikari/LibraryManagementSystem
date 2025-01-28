import time
import click
from tabulate import tabulate
from pymongo import MongoClient

from config import logging_module
from config import verify_jwt_token
from src.admin.stock_book import find_keys


logger = logging_module()

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def user_issue_books_list() -> None:
    user_details = verify_jwt_token()
    username = user_details['username']
    email = user_details['email']
    category_key = find_keys()
    for category in category_key:
        check_book = db.Books.aggregate([
                {'$unwind': f'${category}'},
                {'$unwind': f'${category}.UserDetails'},
                {'$match': {f'{category}.UserDetails.Username': username}}
        ])
    category_check = list(check_book)
    if not category_check:
        return False
    fetch_issue_books = []
    for category_keys in category_key:
        result = db.Books.aggregate([
            {'$unwind': f'${category_keys}'},
            {'$unwind': f'${category_keys}.UserDetails'},
            {
                '$match': {
                    f'{category_keys}.UserDetails.Username': username,
                    f'{category_keys}.UserDetails.Email': email
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'Id': f'${category_keys}.Id',
                    'Title': f'${category_keys}.Title',
                    'Author': f'${category_keys}.Author',
                }
            }
        ])
        for book in result:
            fetch_issue_books.append({
                'Category': category_keys,
                'Id': book['Id'],
                'Title': book['Title'],
                'Author': book['Author']
            })
    table = []
    header = ['Categories', 'Id', 'Title', 'Author']
    for book in fetch_issue_books:
        table.append([
            book['Category'].capitalize(),
            book['Id'],
            book['Title'].capitalize(),
            book['Author'].capitalize()
        ])
    click.echo(tabulate(table, headers=header, tablefmt='mixed_grid'))
    return True


def return_books() -> None:
    is_books_empty = user_issue_books_list()
    if not is_books_empty:
        click.echo('Books list is empty, exiting...')
        time.sleep(2)
        return
    input_categories = click.prompt('Enter Book Category', type=str).lower()
    input_book_id = click.prompt('Enter Book Id', type=int)
    user_details = verify_jwt_token()
    if not user_details:
        time.sleep(1)
        return
    username = user_details['username']
    email = user_details['email']
    # fetch data or remove data like this code
    # don't use other method to remove this type of nested data.
    result = db.Books.update_one(
        {
            f'{input_categories}.Id': input_book_id,
            f'{input_categories}.UserDetails.Username': username,
            f'{input_categories}.UserDetails.Email': email,
        }, {
            # remove data from nested database
            '$pull': {
                f'{input_categories}.$.UserDetails': {
                    'Username': username,
                    'Email': email
                }
            },
            # increase Available book by 1
            '$inc': {
                f'{input_categories}.$.Available': 1
            }
        }
    )

    if result.modified_count > 0:
        click.echo('You Successfully return books')
    else:
        click.echo('Unable to return books, Books not found')


if __name__ == '__main__':
    user_issue_books_list()
