from add_books import AddBooks

import click
import os
import logging

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log_dir = os.path.join(path, 'logs')
os.makedirs(log_dir, exist_ok=True)     # create dir if not exist
log_path = os.path.join(log_dir, 'log_file.log')

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s: %(message)s',
    filename=log_path,
    filemode='a'
    )
logger = logging.getLogger(__name__)


@click.command()
@click.option('--choose', prompt='1. AddBooks\n2. ListBooks\n3. IssueBooks\n4. ReturnBooks\n0. EXIT \n\nChoose 0-4', type=click.IntRange(0, 4), help='Choose between [ 0-4 ]')
def menu(choose: int):
    try:
        match choose:
            case 1:
                add_books()
            case 2:
                list_books()
            case 3:
                issue_books()
            case 4:
                return_books()
            case 0:
                click.echo('Thank You For Your Time.')
                exit()
            case _:
                click.echo('Please Input 1 to 4.')
    except ValueError:
        click.echo('Please Input 0 to 4.')
    except (KeyboardInterrupt, EOFError):
        click.echo('Invalid Method to Quit Program. type 0 for exit')

def add_books() -> None:
    add_books = AddBooks()
    add_books.add()
    logger.info('Adding Books')

def list_books() -> None:
    logger.info('Listing Books')

def issue_books() -> None:
    logger.info('Issuing Books')

def return_books() -> None:
    logger.info('Returning Books')


if __name__ == '__main__':
    menu()