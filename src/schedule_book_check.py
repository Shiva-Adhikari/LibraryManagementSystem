import os
import ssl
import time
import click
import smtplib
import schedule
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient
from email.message import EmailMessage
from dotenv import load_dotenv


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def due_book_check():
    fetch_data = db.Books.find({})
    today_date_ = datetime.now()
    today_date = datetime.date(today_date_)
    if fetch_data:

        for data in fetch_data:
            keys = data.keys() - {'_id'}
            # get one by one and it hold until previous is completed
            categories = next(iter(keys))
            books = data[categories]

            for book in books:
                if 'IssueDate' in book:
                    due_warning = book['DueWarning']
                    due_warning_day = datetime.date(due_warning)
                    due_date = book['DueDate']
                    due_date_day = datetime.date(due_date)

                    if today_date == due_warning_day:
                        user_username = book['Details']['username']
                        user_email = book['Details']['email']
                        due_warning_text = 'DueWarning'

                        send_email(user_username, user_email, due_warning_text)
                    if today_date == due_date_day:
                        user_username = book['Details']['username']
                        user_email = book['Details']['email']
                        due_date_text = 'DueDate'
                        send_email(user_username, user_email, due_date_text)


def send_email(user_username, user_email, due_warning_text):
    load_dotenv()
    email_sender = os.getenv('sender_email')
    email_sender_password = os.getenv('sender_password')
    email_receiver = user_email

    if due_warning_text == 'DueWarning':
        subject = 'Return your library book - 3 days left'
        body = f'Dear {user_username},\n',
        'Your library book is due in 3 days. ',
        'Please return it on time to avoid a Rs.500 late fee.\n',
        'Thank you,\nLIBRARY'

    if due_warning_text == 'DueDate':
        subject = 'Library Book Overdue'
        body = f'Dear {user_username},\n',
        'Your library book is now overdue.',
        ' Please return it immediately.',
        'A late fee of Rs.500 has been added to your account.\n',
        'Thank you,\nLIBRARY'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # establish tls/ssl connection
    context = ssl.create_default_context()

    try:
        # with help to properly close connection
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_sender_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
    except smtplib.SMTPRecipientsRefused:
        click.echo('Email not Valid')


def sleep_time():
    now = datetime.now()
    next_time = now.replace(hour=0, minute=1, second=0, microsecond=0)

    if now > next_time:
        next_time += timedelta(days=1)

    return (next_time - now).seconds


if __name__ == '__main__':
    while True:
        s_t = sleep_time()
        time.sleep(s_t)
        schedule.every().day.at('00:1').do(due_book_check)
        time.sleep(5)
        schedule.run_pending()
