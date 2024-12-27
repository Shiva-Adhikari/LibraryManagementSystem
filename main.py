import src.add_books
import src.issue_books
import src.return_books

import click
import os
import logging


def log_path():
    root_path = os.path.join(os.path.dirname(__file__))
    log_dir = os.path.join(root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)     # create dir if not exist
    log_path = os.path.join(log_dir, 'log_file.log')

    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s %(levelname)s: %(message)s',
        filename=log_path,
        filemode='a'
        )
    logger = logging.getLogger(__name__)
    return logger

logger = log_path()

@click.command()
@click.option('--choose', 
    prompt='1. AddBooks\n2. ListBooks\n3. IssueBooks\n4. ReturnBooks\n0. EXIT \n\nChoose 0-4', 
    type=click.IntRange(0, 4), help='Choose between [ 0-4 ]')
def menu(choose: int):
    try:
        match choose:
            case 1:
                logger.info('Adding Books')
                src.add_books.main()
            case 2:
                logger.info('Listing Books')
                # src.issue_books.main()

            case 3:
                logger.info('Issuing Books')
                src.issue_books.main()

            case 4:
                logger.info('Returning Books')
                src.return_books.main()

            case 0:
                click.echo('Thank You For Your Time.')
                logger.info('EXIT Books')
                exit()
            case _:
                click.echo('Please Input 1 to 4.')
    except ValueError:
        click.echo('Please Input 0 to 4.')
    except (KeyboardInterrupt, EOFError):
        click.echo('Invalid Method to Quit Program. type 0 for exit')


if __name__ == '__main__':
    menu()