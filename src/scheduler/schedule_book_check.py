# third party modules
from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore

# built in modules
import ssl
import smtplib
from datetime import datetime
from email.message import EmailMessage

# local modules
from src.utils import find_keys
from src.models import settings, db


def mail_box(user_username, subject_filled, body_filled):
    """html and css is added to show to users in mail

    Args:
        user_username (str): username
        subject_filled (str): subject of mail
        body_filled (str): text body

    Return:
        subject (str): subject
        body (str): html body
    """
    subject = f'{subject_filled}'
    body = f'''
    <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Arial', sans-serif; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
            <h1>Library Reminder</h1>
        </div>
        <div style="padding: 30px;">
            <div style="background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                <strong>{subject_filled}</strong>
            </div>
            <h2>Dear {user_username}</h2>
            <p>{body_filled}</p>
            <strong>Thank You</strong><br>
            <strong>LIBRARY</strong>
        </div>
    </div>
</body>
</html>
    '''
    return subject, body


def due_book_check():
    """if date is 3 days left or due date it send email to users in mailbox.
    """
    category_key = find_keys()
    today_date_ = datetime.now()
    today_date = datetime.date(today_date_)
    for category in category_key:
        fetch_data = db.Books.aggregate([
            {'$unwind': f'${category}'},
            {'$unwind': f'${category}.UserDetails'},
            {
                '$match': {
                        f'{category}.UserDetails.IssueDate': {
                            '$lte': today_date_
                        }
                }
            },
            {
                '$project': {
                    'Username': f'${category}.UserDetails.Username',
                    'Email': f'${category}.UserDetails.Email',
                    # 'DueWarning': f'${category}.UserDetails.IssueDate',   # for testing purpose
                    'DueWarning': f'${category}.UserDetails.DueWarning',
                    'DueDate': f'${category}.UserDetails.DueDate'
                }
            }
        ])
        for book in fetch_data:
            due_warning = book['DueWarning']
            due_warning_day = datetime.date(due_warning)
            due_date = book['DueDate']
            due_date_day = datetime.date(due_date)

            if today_date == due_warning_day:
                user_username = book['Username']
                user_email = book['Email']
                due_warning_text = 'DueWarning'
                send_email(user_username, user_email, due_warning_text)
            if today_date == due_date_day:
                user_username = book['Username']
                user_email = book['Email']
                due_date_text = 'DueDate'
                send_email(user_username, user_email, due_date_text)


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
        body_filled = 'Your library book is due in 3 days. Please return it on time to avoid a Rs.500 late fee.'
        subject, body = mail_box(user_username, subject_filled, body_filled)

    if due_text == 'DueDate':
        subject_filled = 'Library Book Overdue'
        body_filled = 'Your library book is now overdue. Please return it immediately. A late fee of Rs.500 has been added to your account.'
        subject, body = mail_box(user_username, subject_filled, body_filled)

    em = EmailMessage()
    em['From'] = SENDER_EMAIL
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body, subtype='html')

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


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(due_book_check, 'cron', hour=0)   # run every midnight
    # scheduler.add_job(due_book_check, 'cron', minute="*")   # run every minute    # for testing purpose
    scheduler.start()
