import smtplib, ssl
from email.message import EmailMessage

def send_email(receiver, message):
    sender = "yuyuanwang1999@gmail.com"
    password = "ytpuqhpomlekpeqh"
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()
    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = 'Agmnitor Notification'
    msg['From'] = sender
    msg['To'] = receiver

    # Send the message via our own SMTP server.
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)


if __name__ == "__main__":
    
    receiver = "kaiwen_li@ucsb.edu"
    message = "Hello, this is a test email"
    send_email(receiver, message)
