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
    msg.add_alternative("""\
    <html>
    <head></head>
    <body>
        <p style="font-size:22px" >{}
        </p>
        <br/>
        <p style="font-size:22px">SmartGrid Team</p>
        <p style="font-size:22px">ucsbsmartgrid@gmail.com</p>

    </body>
    </html>
    """.format(message), subtype='html')


    msg['Subject'] = 'Your Changes for SmartGrid Optimization'
    msg['From'] = "SmartGrid Optimization AutoNotification"
    msg['To'] = receiver

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, password)
    s.send_message(msg)
    s.quit()

