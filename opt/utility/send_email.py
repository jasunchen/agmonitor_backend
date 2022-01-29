import smtplib, ssl

def send_email(receiver):
    sender = "yuyuanwang1999@gmail.com"
    password = "ytpuqhpomlekpeqh"
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    messages = """\
    Subject: Hi there
    This message is sent from Python."""
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, messages)


if __name__ == "__main__":
    
    receiver = "alexmei@ucsb.edu"
    send_email(receiver)
