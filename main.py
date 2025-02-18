import time
import click

from concurrent.futures import ThreadPoolExecutor

from src.user.list_books import list_books
from src.user.issue_books import issue_books
from src.user.user_account import user_login
from src.user.return_books import return_books
from src.user.user_account import user_register
from src.admin.add_books import add_books
from src.admin.stock_book import stock_book
from src.admin.search_books import search_books
from src.admin.update_books import update_books
from src.admin.delete_books import delete_books
from src.admin.admin_account import admin_login
from src.admin.admin_account import admin_register
from config import logout
from config import tqdm_progressbar
from config import verify_jwt_token
from config import get_user_login_details
from config import get_admin_login_details
from config import remove_user_login_details
from config import remove_admin_login_details
from config import validate_access_token
from config import token_blacklist


"""global variable"""
logged_as_user = get_user_login_details()
logged_as_admin = get_admin_login_details()


@click.command()
@click.option(
    '--choose',
    prompt='1. Register Admin Account\n2. Login Admin Account\n0. Exit\n',
    type=int
)
def admin_accounts(choose: int):
    click.clear()
    global logged_as_user
    global logged_as_admin
    match choose:
        case 1:
            if logged_as_user:
                click.echo('You are a USER, unable to register as Admin')
            else:
                admin_register()
        case 2:
            if logged_as_admin:
                click.echo('You are already a Admin. Unable to login twice.')
            else:
                check_login = admin_login()
                if check_login:
                    remove_user_login_details()
                    logged_as_admin = True
                    logged_as_user = False
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")
    time.sleep(2)
    click.clear()
    library()


@click.command()
@click.option(
    '--choose',
    prompt='1. Register User Account\n2. Login User Account\n0. Exit\n',
    type=int
)
def user_accounts(choose: int):
    global logged_as_admin
    global logged_as_user
    match choose:
        case 1:
            if logged_as_admin:
                user_register()
            else:
                click.echo('You are not a Admin User to Create Account')
        case 2:
            if logged_as_user:
                click.echo('You are already a User. Unable to login twice.')
            else:
                check_login = user_login()
                if check_login:
                    remove_admin_login_details()
                    logged_as_user = True
                    logged_as_admin = False
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")
    time.sleep(2)
    click.clear()
    library()


@click.command()
@click.option(
    '--choose',
    prompt='1. Create Books\n2. Search Books\n3. Stock Books\n'
    '4. Update Books\n5. Remove Books\n0. Exit\n',
    type=int
)
def admin_list_books(choose: int):
    global logged_as_admin
    global logged_as_user
    match choose:
        case 1:
            verify = verify_jwt_token()
            if verify:
                add_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 2:
            verify = verify_jwt_token()
            if verify:
                search_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 3:
            verify = verify_jwt_token()
            if verify:
                stock_book()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 4:
            verify = verify_jwt_token()
            if verify:
                update_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 5:
            verify = verify_jwt_token()
            if verify:
                delete_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")
    verify_jwt_token()
    time.sleep(1)
    click.clear()
    library()


@click.command()
@click.option(
    '--choose',
    prompt='1. Issue Books\n2. List Books\n3. Return Books\n0. Exit\n',
    type=int
)
def user_list_books(choose: int):
    global logged_as_admin
    global logged_as_user
    match choose:
        case 1:
            verify = verify_jwt_token()
            if verify:
                issue_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 2:
            verify = verify_jwt_token()
            if verify:
                list_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 3:
            verify = verify_jwt_token()
            if verify:
                return_books()
            else:
                logged_as_admin = False
                logged_as_user = False
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")
    verify_jwt_token()
    time.sleep(1)
    click.clear()
    library()


@click.command()
@click.option(
    '--choose',
    prompt='1. Admin Account\n2. User Account\n3. LogOut\n0. Exit\n',
    type=int
)
def show_accounts(choose: int):
    """Show Admin, User Accounts"""
    global logged_as_admin
    global logged_as_user
    click.clear()
    match choose:
        case 1:
            admin_accounts()

        case 2:
            user_accounts()

        case 3:
            token = validate_access_token()
            if not token:
                token_blacklist()
            logout()
            logged_as_user = False
            logged_as_admin = False
            click.echo('Logging out...')

        case 0:
            exit()
        case _:
            click.echo("Invalid Input")
    time.sleep(2)
    click.clear()
    library()


@click.command()
@click.option(
    '--choose',
    prompt='1. Manage Account\n2. View Books\n0. Exit\n',
    type=int
)
def library(choose: int):
    click.clear()
    global logged_as_admin
    global logged_as_user
    match choose:
        case 1:
            show_accounts()
        case 2:
            verify = verify_jwt_token()
            if verify:
                if logged_as_user:
                    user_list_books()
                elif logged_as_admin:
                    admin_list_books()

            else:
                click.echo(
                        'You are not loggedin. Please login first'
                    )
                logged_as_admin = False
                logged_as_user = False

        case 0:
            exit()
        case _:
            click.echo("Invalid Input")
    time.sleep(2)
    click.clear()
    library()


def run():
    click.clear()
    tqdm_progressbar()
    click.clear()
    library()


def main():
    global logged_as_user
    global logged_as_admin
    with ThreadPoolExecutor() as executor:
        executor.submit(run)
        verify = executor.submit(verify_jwt_token)
        if verify.result():
            is_it = validate_access_token()
            if is_it:
                logout()

            else:
                logged_as_user = False
                logged_as_admin = False
        else:
            logged_as_user = False
            logged_as_admin = False


if __name__ == '__main__':
    main()
