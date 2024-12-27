from pathlib import Path
import click
import json


library_books = Path('data/LibraryBooks.json').resolve()

def process_book(categories_check, input_book_id, available, set_available):
    categories_check = categories_check.lower()
    with open(library_books, 'r', encoding='utf-8') as file:
        categories = json.load(file)
    for books_keys, books_values in categories.items():
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
@click.option('--categories_check', prompt=('Enter Book Category'), type=str)
@click.option('--input_book_id', prompt=('Enter Book Id'), type=int)
def _issue_books(categories_check, input_book_id):
    process_book(categories_check, input_book_id, 1, 0)

def main():
    _issue_books()

if __name__ == '__main__':
    main()