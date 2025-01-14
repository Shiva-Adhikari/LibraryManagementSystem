from tabulate import tabulate
from pymongo import MongoClient
import click


books_keys = []

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def connect_database():
    fetch_books = db.Books.find({}, {'_id': 0})
    for fetch_keys in fetch_books:
        books_keys.append(list(fetch_keys.keys()))
    if books_keys:
        return books_keys
    else:
        return False


def list_books():
    books_keys = connect_database()
    if not books_keys:
        click.echo('Books list is empty')
        return
    category = click.prompt(
        'Enter book category',
        type=str,
        default=books_keys
    )
    page_no = click.prompt('Enter page number', type=int)
    check_true = True
    while True:
        check_true = list_view(category, page_no)
        if check_true is False:
            break
        ask = input('next page? (yes/No)\n-> ').strip().lower()
        if ask == 'yes':
            page_no += 1
            continue
        else:
            break


def list_view(category: str, page_no: int) -> bool:
    """list books from database"""
    count_books = db.Books.aggregate([
        {'$unwind': f'${category}'},
        {'$count': 'total'}
    ]).next()['total']
    page_size = 5  # Number of elements per page
    total_pages = (count_books + page_size - 1) // page_size
    if page_no < 1 or page_no > total_pages:
        click.echo(f'Invalid page, Available pages up to {total_pages}')
        return False
    skip_line = (page_no - 1) * page_size     # Calculate skip value
    pipeline = [
        {'$match': {category: {'$exists': True}}},
        {'$unwind': f'${category}'},
        {'$skip': skip_line},
        {'$limit': page_size}
    ]
    find_books_page_1 = list(db.Books.aggregate(pipeline))

    header = ['Id', 'Title', 'Author', 'Available']
    table = []
    for extract in find_books_page_1:
        table.append([
            extract[category]['Id'],
            extract[category]['Title'].capitalize(),
            extract[category]['Author'].capitalize(),
            'Yes' if extract[category]['Available'] else 'No'
        ])
    click.echo(tabulate(table, headers=header, tablefmt='mixed_grid'))
    click.echo(f'\nPage {page_no} of {total_pages}')

    global books_keys
    books_keys = []
