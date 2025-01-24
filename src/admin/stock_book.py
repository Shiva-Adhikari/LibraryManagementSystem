import click
from tabulate import tabulate
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def find():
    results = db.Books.find()
    for result in results:
        category_keys = next(iter(result.keys() - {'_id': 0}))
        print(f'keys:{category_keys}')
    return category_keys


def stock_book():
    category = find()
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

    table = []
    for result in results:
        header = ['Category', 'Title', 'Available']
        table.append([
            category.capitalize(),
            result['Title'].capitalize(),
            result['Available']
        ])

    click.echo(tabulate(table, headers=header, tablefmt='mixed_grid'))
    input('\nPress Any Key...')


if __name__ == '__main__':
    stock_book()
