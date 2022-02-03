from twilio.rest import Client
import environ

env = environ.Env()


def send_message(mes, phone_number):
    account = env('ACCOUNT')
    token = env('TOKEN')
    client = Client(account, token)
    to_number = '+1' + phone_number
    from_number = env('PHONE_NUMBER')

    message = client.messages.create(to=to_number, from_=from_number, body=mes)

if __name__ == "__main__":
    send_message("Hello", "6263619710")