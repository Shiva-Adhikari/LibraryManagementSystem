import os
import ssl
import smtplib
from datetime import datetime
from email.message import EmailMessage
from src.admin.stock_book import find_keys
from html_body import mail_box

from dotenv import load_dotenv
from pymongo import MongoClient
from apscheduler.schedulers.blocking import BlockingScheduler


client = MongoClient('localhost', 27017)
db = client.LibraryManagementSystem


def due_book_check():
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
    load_dotenv()
    email_sender = os.getenv('sender_email')
    email_sender_password = os.getenv('sender_password')
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
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body, subtype='html')

    # establish tls/ssl connection
    context = ssl.create_default_context()

    try:
        # with help to properly close connection
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_sender_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
    except smtplib.SMTPRecipientsRefused:
        # click.echo('Email not Valid')
        pass


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(due_book_check, 'cron', hour=0)   # run every midnight
    # scheduler.add_job(due_book_check, 'cron', minute="*")   # run every minute    # for testing purpose
    scheduler.start()
