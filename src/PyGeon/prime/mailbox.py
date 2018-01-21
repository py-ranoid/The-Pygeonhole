import requests
import markdown
from prime.data import MAILGUN_KEY
# from data import MAILBOX_KEY
# headers = {
#     'Authorization': MAILBOX_KEY,
#     'Content-Type': 'application/json',
# }

# cont = open('email_trial.html').read()
# cont


def send(subject='Wasssup', text='## Bingo'):
    body = markdown.markdown(text)
    data = '{"personalizations": [{"to": [{"email": "vishstar88@gmail.com"}]}], "from": {\
        "email": "sendeexampexample@example.com"}, "subject": "%s", "content": [{"type": "text/html", "value": "%s"}]}'

    print (requests.post('https://api.sendgrid.com/v3/mail/send',
                         headers=headers, data=data % (subject, body)))


def send_simple_message(subject="Your Pygeon has arrived", body="Congratulations Vishal, you just sent an email with Mailgun!  You are truly awesome!", to="Vishal <vishstar88@gmail.com>"):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox37bd14349c8749d8a9b7dec8d8996261.mailgun.org/messages",
        auth=("api", MAILGUN_KEY),
        data={"from": "Pygeon master <vishalg8897@gmail.com>",
              "to": to,
              "subject": subject,
              "html": body})


# print (send())
# x = send_simple_message(body=cont)
# x.content
