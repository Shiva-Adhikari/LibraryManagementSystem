from admin import password_validation
from email_validator import validate_email, EmailNotValidError
import click


@click.command
@click.option('--username', prompt='Enter Username', type=str)
def validation(username: str):
    # get email
    email = email_validation()
    # get password
    password = password_validation()
    # now place in mongodb


def email_validation() -> str:
    while True:
        email = click.prompt('Enter Email: ', type=str)
        try:
            email = validate_email(email, check_deliverability=False)
            email = email.normalized
            return email
        except EmailNotValidError as e:
            print(str(e))


def main():
    validation()


if __name__ == '__main__':
    main()
