from issue_books import process_book 
import click


@click.command()
@click.option('--categories_check', prompt=('What type of Books you need'), type=str)
@click.option('--input_book_id', prompt=('Enter Book Id'), type=int)
def return_books(categories_check, input_book_id):
    process_book(categories_check, input_book_id, 0, 1)


def main():
    return_books()

if __name__ == '__main__':
    main()