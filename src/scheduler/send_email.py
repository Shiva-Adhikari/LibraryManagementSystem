# third party modules
from jinja2 import FileSystemLoader, Environment

# built in modules
import ssl
import smtplib
from email.message import EmailMessage

# local modules
from src.models import settings


env = Environment(loader=FileSystemLoader('scheduler'))


def render_template(user_username, subject_filled, body_filled):
    template = env.get_template('email_template.html')
    return template.render(
        user_username=user_username,
        subject_filled=subject_filled,
        body_filled=body_filled
    )


def send_email(user_username, user_email, due_text):
    """this send message in mailbox

    Args:
        user_username (str): username
        user_email (str): email
        due_text (text): message to user
    """
    SENDER_EMAIL = settings.SENDER_EMAIL.get_secret_value()
    SENDER_PASSWORD = settings.SENDER_PASSWORD.get_secret_value()
    email_receiver = user_email

    if due_text == 'DueWarning':
        subject_filled = 'Return your library book - 3 days left'
        body_filled = (
            'Your library book is due in 3 days. '
            'Please return it on time to avoid a Rs.500 late fee.'
        )

    elif due_text == 'DueDate':
        subject_filled = 'Library Book Overdue'
        body_filled = (
            'Your library book is now overdue. '
            'Please return it immediately. '
            'A late fee of Rs.500 has been added to your account.'
        )

    else:
        return

    html_content = render_template(user_username, subject_filled, body_filled)

    em = EmailMessage()
    em['From'] = SENDER_EMAIL
    em['To'] = email_receiver
    em['Subject'] = subject_filled
    em.set_content(html_content, subtype='html')

    # establish tls/ssl connection
    context = ssl.create_default_context()

    try:
        # with help to properly close connection
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.sendmail(SENDER_EMAIL, email_receiver, em.as_string())
    except smtplib.SMTPRecipientsRefused:
        # click.echo('Email not Valid')
        pass
