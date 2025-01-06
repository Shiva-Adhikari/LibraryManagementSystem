import click
from src.admin import admin_register, admin_login
from src.user import user_register, user_login


logged_as_user = None
logged_as_admin = None


@click.command()
@click.option(
    '--choose',
    prompt='1. Manage Account\n2. View Books\n0. Exit\n',
    type=int
)
def create_account(choose: int) -> int:
    match choose:
        case 1:
            click.echo("create account")
            show_accounts()
        case 2:
            click.echo("viewbooks")
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
def admin_accounts(choose: int) -> int:
    match choose:
        case 1:
            click.echo("register admin account")
            admin_register()

        case 2:
            click.echo("login admin account")
            admin_login()

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
def user_accounts(choose: int) -> int:
    match choose:
        case 1:
            click.echo("register user account")
            user_register()
        case 2:
            click.echo("login user account")
            user_login()
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
def show_accounts(choose: int) -> int:
    match choose:
        case 1:
            click.echo("call admin account")
            admin_accounts()
            # for login or signup
        case 2:
            click.echo("call user account")
            user_accounts()
            # for login or signup
        case 0:
            exit()
        case _:
            click.echo("Invalid Input")


def main():
    create_account()


if __name__ == '__main__':
    main()
