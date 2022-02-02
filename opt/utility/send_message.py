from twilio.rest import Client


def send_message(mes, phone_number):
    account = "ACXXXXXXXXXXXXXXXXX"
    token = "YYYYYYYYYYYYYYYYYY"
    client = Client(account, token)

    message = client.messages.create(to=phone_number, from_="+15555555555", body=mes)