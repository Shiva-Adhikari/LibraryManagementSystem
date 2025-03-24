# third party modules
from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore

# built in modules
from datetime import datetime

# local modules
from src.utils import find_keys
from src.models import db
from .send_email import send_email


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


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(due_book_check, 'cron', hour=0)   # run every midnight
    # scheduler.add_job(due_book_check, 'cron', minute="*")   # run every minute    # for testing purpose
    scheduler.start()
