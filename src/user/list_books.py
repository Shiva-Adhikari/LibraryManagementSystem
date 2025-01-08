from pymongo import MongoClient
import click


books_keys = []

client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem
fetch_books = db.Books.find({}, {'_id': 0})
for fetch_keys in fetch_books:
    books_keys.append(list(fetch_keys.keys()))


@click.command()
@click.option(
    '--category',
    prompt='Enter book category',
    type=str,
    default=books_keys
)
@click.option('--page', prompt='Enter page number', type=int)
def list_books(category: str, page: int) -> None:
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

    for extract in find_books_page_1:
        print(f"Id: {extract[category]['Id']}")
        print(f"Title: {extract[category]['Title']}")
        print(f"Author: {extract[category]['Author']}")
        print(f"Available: {extract[category]['Available']}")
        print()


if __name__ == '__main__':
    list_books()
