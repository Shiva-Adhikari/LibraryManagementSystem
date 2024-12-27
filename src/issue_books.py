from pathlib import Path
import click
import json


library_books = Path('data/LibraryBooks.json').resolve()

def process_book(input_categories, input_book_id, available, set_available):
    input_categories = input_categories.lower()
    with open(library_books, 'r', encoding='utf-8') as file:
        categories = json.load(file)
    for books_keys, books_values in categories.items():
        # print(books_keys)
        # print(books_values)
        if input_categories == books_keys:
            # print(books_keys)
            for books in books_values:
                if input_book_id == books['Id']:
                    if books['Available'] == available:
                        books['Available'] = set_available
                        with open(library_books, 'w', encoding='utf-8') as file:
                            json.dump(categories, file, indent=4)
                            click.echo('Data Successfully Saved in File\n')
                            return
                    else:
                        click.echo('Books Not Available')
                        return
            if len(books_values):
                click.echo('Invalid ID.')
                

@click.command()
@click.option('--input_categories', prompt=('Enter Book Category'), type=str)
@click.option('--input_book_id', prompt=('Enter Book Id'), type=int)
def _issue_books(input_categories, input_book_id):
    process_book(input_categories, input_book_id, 1, 0)     # available=1     # set-available = 0

def main():
    _issue_books()
