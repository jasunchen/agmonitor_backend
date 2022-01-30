from opt.utility.send_email import send_email
# from ucsb.models import *
from apscheduler.schedulers.background import BackgroundScheduler

from pytz import utc

def opt_scheduler():
    from ucsb.models import user
    users = user.objects.all()
    for user in users:
        receiver = user.user_email
        message = "Hello, this is a test email"
        send_email(receiver, message)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(opt_scheduler, 'cron', hour=21, minute=00, timezone='America/Los_Angeles')
    scheduler.start()