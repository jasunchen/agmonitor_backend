from opt.utility.send_email import send_email

def opt_scheduler():
    receiver = "kaiwen_li@ucsb.edu"
    message = "Hello, this is a test email"
    send_email(receiver, message)