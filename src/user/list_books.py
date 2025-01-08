from tabulate import tabulate
from pymongo import MongoClient
import click


books_keys = []

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem
fetch_books = db.Books.find({}, {'_id': 0})
for fetch_keys in fetch_books:
    books_keys.append(list(fetch_keys.keys()))


# @click.command()
# @click.option(
    # '--category',
    # prompt='Enter book category',
    # type=str,
    # default=books_keys
# )
# @click.option('--page', prompt='Enter page number', type=int)
def list_books():
    category = click.prompt('Enter book category', type=str, default=books_keys)
    page = click.prompt('Enter page number', type=int)
    while True:
        # page = page
        list_view(category, page)
        ask = input('Again? Yes/no\n-> ').strip().lower()
        if ask == 'yes':
            page += 1
            continue
        else:
            break


def list_view(category: str, page: int) -> None:
    """list books from database"""
    page_number = page
    page_size = 5  # Number of elements per page
    skip_line = (page_number - 1) * page_size     # Calculate skip value
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
            extract[category]['Title'],
            extract[category]['Author'],
            'Yes' if extract[category]['Available'] else 'No'
        ])
    print(tabulate(table, headers=header, tablefmt='mixed_grid'))


if __name__ == '__main__':
    list_books()
