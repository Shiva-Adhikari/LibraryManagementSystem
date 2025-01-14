import click
import time

from src.admin.admin_account import admin_register
from src.admin.admin_account import admin_login
from src.admin.add_books import add_books
from src.admin.search_books import search_books
from src.admin.update_books import update_books
from src.admin.delete_books import delete_books
from src.user.user_account import user_register
from src.user.user_account import user_login
from src.user.issue_books import issue_books
from src.user.list_books import list_books
from src.user.return_books import return_books
from config import get_user_login_details
from config import remove_user_login_details
from config import get_admin_login_details
from config import remove_admin_login_details


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
    match choose:
        case 1:
            global logged_as_user
            global logged_as_admin
            if logged_as_user:
                click.echo('You are a USER, unable to register as Admin')
            else:
                admin_register()
            time.sleep(2)
            click.clear()
            library()

        case 2:
            if logged_as_admin:
                click.echo('You are already a Admin. Unable to login twice.')
            else:
                check_login = admin_login()
                if check_login:
                    remove_user_login_details()
                    logged_as_admin = True
                    logged_as_user = False
            time.sleep(2)
            click.clear()
            library()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Register User Account\n2. Login User Account\n0. Exit\n',
    type=int
)
def user_accounts(choose: int):
    match choose:
        case 1:
            global logged_as_admin
            global logged_as_user
            if logged_as_admin:
                user_register()
                """ user progress bar """
            else:
                click.echo('You are not a Admin User to Create Account')
            time.sleep(2)
            click.clear()
            library()
        case 2:
            if logged_as_user:
                click.echo('You are already a User. Unable to login twice.')
                time.sleep(2)
                click.clear()
                library()
            check_login = user_login()
            if check_login:
                remove_admin_login_details()
                logged_as_user = True
                logged_as_admin = False
            time.sleep(2)
            click.clear()
            library()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Create Books\n2. Search Books\n'
    '3. Update Books\n4. Remove Books\n0. Exit\n',
    type=int
)
def admin_list_books(choose: int):
    """ use while loop """
    match choose:
        case 1:
            add_books()
            time.sleep(1)
            click.clear()
            library()
        case 2:
            search_books()
            time.sleep(1)
            click.clear()
            library()
        case 3:
            update_books()
            time.sleep(1)
            click.clear()
            library()
        case 4:
            delete_books()
            time.sleep(1)
            click.clear()
            library()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Issue Books\n2. List Books\n3. Return Books\n0. Exit\n',
    type=int
)
def user_list_books(choose: int):
    match choose:
        case 1:
            issue_books()
            time.sleep(1)
            click.clear()
            library()
        case 2:
            list_books()
            time.sleep(1)
            click.clear()
            library()
        case 3:
            return_books()
            time.sleep(1)
            click.clear()
            library()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Admin Account\n2. User Account\n3. LogOut\n0. Exit\n',
    type=int
)
def show_accounts(choose: int):
    """Show Admin, User Accounts"""
    click.clear()
    match choose:
        case 1:
            admin_accounts()
            click.clear()
        case 2:
            user_accounts()
            click.clear()
        case 3:
            remove_user_login_details()
            remove_admin_login_details()
            click.echo('Logging out...')
            time.sleep(1)
            click.clear()
            library()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Manage Account\n2. View Books\n0. Exit\n',
    type=int
)
def library(choose: int):
    click.clear()
    match choose:
        case 1:
            show_accounts()
            click.clear()
        case 2:
            if logged_as_user:
                user_list_books()
            if logged_as_admin:
                admin_list_books()
            else:
                click.echo(
                    'You are not loggedin. Please login first'
                )
                time.sleep(2)
                click.clear()
                library()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


def main():
    library()


if __name__ == '__main__':
    main()
