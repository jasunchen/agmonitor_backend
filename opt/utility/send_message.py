from twilio.rest import Client


def send_message(mes, phone_number):
    account = "ACb7aa0b75ba44f21340d4ddf870cfac3a"
    token = "1b336073000ea39f2abae91c961d5c1b"
    client = Client(account, token)
    to_number = '+1' + phone_number

    message = client.messages.create(to=to_number, from_="+19034597869", body=mes)

if __name__ == "__main__":
    send_message("Hello", "6263619710")