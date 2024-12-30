from pathlib import Path
import click
import json
import os

# get library json file ( get absolute path )
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_dir = os.path.join(root_path, 'data/')
os.makedirs(data_dir, exist_ok=True)     # create dir if not exist
data_path = os.path.join(data_dir, 'LibraryBooks.json')
library_books = Path(data_path)

def check_file(library_books):
    """Fetch Data"""
    try:
        with open(library_books, 'r', encoding='utf-8') as file:
            categories = json.load(file)
            return categories
    except FileNotFoundError:
        print(f"Error: {library_books} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: {library_books} is not a valid JSON file.")
        return {}

categories = check_file(library_books)
category_keys = list(categories.keys())
@click.command()
@click.argument('category_key', type=click.Choice(category_keys, case_sensitive=False))
@click.option('--page', default=1, prompt='Enter page number', help='Page number')
@click.option('--per-page', default=2, prompt='how many items per page', help='Items per page')
def show_books(category_key, page, per_page):
    """Pagination Calculate"""
    # get list of books
    books = categories[category_key]
    # get total pages
    total_pages = (len(books) + per_page - 1) // per_page

    # check condition valid or not
    if page < 1 or page > total_pages:
        click.echo(f'Invalid page, Available pages to up {total_pages}')
        return

    # start number
    start = (page - 1) * per_page

    # end number
    end = start + per_page

    # in which page number to start and end
    current_page_books = books[start:end]

    """Display List fo Books"""
    click.echo(f'\nShowing {category_key.upper()} books (page {page})')
    click.echo(' Id | Title     | Author     | Available  ')
    for _ in range(45):
        click.echo('-', nl=False)
    click.echo()
    for book in current_page_books:
        click.echo(f' {book["Id"]:<2} | ',nl=False)
        click.echo(f'{book["Title"].capitalize():<9} | ',nl=False)      # :<9 (9 space allocate)
        click.echo(f'{book["Author"].capitalize():<10} | ',nl=False)
        click.echo('Yes' if book['Available'] else 'No')
    click.echo(f'\nPage {page} of {total_pages}')


if __name__ == '__main__':
    show_books()
