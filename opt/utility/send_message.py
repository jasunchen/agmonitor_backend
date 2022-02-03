from twilio.rest import Client


def send_message(mes, phone_number):
    account = "account"
    token = "token"
    client = Client(account, token)
    to_number = '+1' + phone_number

    message = client.messages.create(to=to_number, from_="number", body=mes)

if __name__ == "__main__":
    send_message("Hello", "6263619710")