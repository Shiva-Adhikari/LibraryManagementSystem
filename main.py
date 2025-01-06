import click
from src.admin import admin_register, admin_login
from src.user import user_register, user_login


logged_as_user = None
logged_as_admin = None


@click.command()
@click.option(
    '--choose',
    prompt='1. Issue Books\n2.Return Books\n0. Exit',
    type=int
)
def user_list_books(choose: int):
    match choose:
        case 1:
            pass
        case 2:
            pass
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Create Books\n2. List Books\n3. Update Books\n4. Remove Books\n'
    '0. Exit',
    type=int
)
def admin_list_books(choose: int):
    match choose:
        case 1:
            pass
        case 2:
            pass
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
def create_account(choose: int):
    match choose:
        case 1:
            click.echo("Managing Account...")
            show_accounts()
        case 2:
            click.echo("List of Books...")
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Register Admin Account\n2. Login Admin Account\n0. Exit\n',
    type=int
)
def admin_accounts(choose: int):
    match choose:
        case 1:
            global logged_as_user
            if logged_as_user is None:
                click.echo("registering admin account...")
                admin_register()
            else:
                click.echo('You are a user Unable to Register as Admin')

        case 2:
            click.echo("logging Admin Account...")
            logged_as_admin = admin_login()
            logged_as_user = None
            input('Login successfully. Press Any Key to Continue')
            admin_list_books()
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
            if logged_as_admin is not None:
                click.echo("registering user account...")
                user_register()
            else:
                click.echo('You are not a Admin User to Create Account')
        case 2:
            click.echo("logging user account...")
            logged_as_user = user_login()
            logged_as_admin = None
            input('Login successfully. Press Any Key to Continue')
            user_list_books()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


@click.command()
@click.option(
    '--choose',
    prompt='1. Admin Account\n2. User Account\n0. Exit\n',
    type=int
)
def show_accounts(choose: int):
    """Show Admin, User Accounts"""
    match choose:
        case 1:
            click.echo("call admin account")
            admin_accounts()
        case 2:
            click.echo("call user account")
            user_accounts()
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


def main():
    create_account()


if __name__ == '__main__':
    main()
