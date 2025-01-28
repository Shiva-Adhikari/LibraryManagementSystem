import time
import click
from tabulate import tabulate
from pymongo import MongoClient

from config import verify_jwt_token


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def find_keys():
    categories = db.Books.find()
    keys = [next(iter(data.keys() - {'_id'})) for data in categories]
    if not keys:
        return False
    return keys


def stock_book():
    verify = verify_jwt_token()
    if not verify:
        time.sleep(1)
        return
    category_key = find_keys()
    if not category_key:
        click.echo('Books Not found, exiting...')
        time.sleep(2)
        return
    append_result = []
    for category in category_key:
        results = db.Books.aggregate([
            {'$unwind': f'${category}'},
            {
                '$match': {
                    f'{category}.Available': {'$lt': 5}
                }
            }, {
                '$project': {
                    'Title': f'${category}.Title',
                    'Available': f'${category}.Available',
                    '_id': 0
                }
            }
        ])
        for result in results:
            append_result.append({
                'Category': category,
                'Title': result['Title'],
                'Available': result['Available'],
            })
    table = []
    for result in append_result:
        table.append([
            result['Category'].capitalize(),
            result['Title'].capitalize(),
            result['Available']
        ])
    header = ['Category', 'Title', 'Available']
    click.echo(tabulate(table, headers=header, tablefmt='mixed_grid'))
    input('\nPress Any Key...')
