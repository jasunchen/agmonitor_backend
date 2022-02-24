import smtplib, ssl
from email.message import EmailMessage
import environ

env = environ.Env()

def send_email(receiver, message):
    sender = "ucsbsmartgrid@gmail.com"
    password = env('SMTPAPIKEY')
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()
    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = 'Your Changes for SmartGrid Optimization'
    msg['From'] = "SmartGrid Optimization AutoNotification"
    msg['To'] = receiver

    # Send the message via our own SMTP server.
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)


if __name__ == "__main__":
    
    receiver = "kaiwen_li@ucsb.edu"
    message = "Hello, this is a test email"
    send_email(receiver, message)
