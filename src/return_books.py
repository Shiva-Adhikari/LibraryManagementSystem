from . import issue_books
import click


@click.command()
@click.option('--categories_check', prompt=('Enter Book Category'), type=str)
@click.option('--input_book_id', prompt=('Enter Book Id'), type=int)
def return_books(categories_check, input_book_id):
    issue_books.process_book(
        categories_check,
        input_book_id,
        0,  # available = 1
        1   # set-available = 0
        )


def main():
    return_books()
