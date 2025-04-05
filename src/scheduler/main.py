# third party modules
from apscheduler.schedulers.blocking import BlockingScheduler

# built in modules
from datetime import datetime

# local modules
from src.models import UserDetails
from src.scheduler.send_email import send_email


def due_book_check():
    """if date is 3 days left or due date it send email to users in mailbox.
    """
    _today_date = datetime.now()
    today_date = datetime.date(_today_date)
    user_details = UserDetails.objects()

    for user in user_details:
        due_warning = user.due_warning
        due_warning_day = datetime.date(due_warning)
        due_date = user.due_date
        due_date_day = datetime.date(due_date)

        if today_date == due_warning_day:
            user_username = user.username
            user_email = user.email
            due_warning_text = 'DueWarning'
            send_email(user_username, user_email, due_warning_text)

        if today_date == due_date_day:
            user_username = user.username
            user_email = user.email
            due_date_text = 'DueDate'
            send_email(user_username, user_email, due_date_text)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(due_book_check, 'cron', hour=0)   # run every midnight
    # scheduler.add_job(due_book_check, 'cron', minute="*/1")   # run every minute    # for testing purpose
    print("Scheduler starting...")
    scheduler.start()
