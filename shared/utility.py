import re
import threading
import phonenumbers

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.validators import ValidationError

email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
phone_regex=re.compile(r"^998([378]{2}|(9[013-57-9]))\d{7}$")


def check_email_or_phone(email_or_phone):
    phone_number = phonenumbers.parse(email_or_phone)
    if re.fullmatch(email_regex,email_or_phone):
        email_or_phone='email'
    elif phonenumbers.is_valid_number(phone_number):
        phone_number=phonenumbers.parse(email_or_phone)
        if phonenumbers.is_valid_number(phone_number):
            email_or_phone='phone'
        else:
            data = {
                'success': False,
                'message': "Telefon raqamningiz noto'g'ri"
            }
            raise ValidationError(data)
    else:
        data={
            'success': False,
            'message': "Email or telefon raqamningiz noto'g'ri"
        }
        raise ValidationError(data)
    return email_or_phone

class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Email:
    @staticmethod
    def send_email(data):
        email=EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type')=='html':
            email.content_subtype='html'
        EmailThread(email).start()

def send_mail(email,code):
    html_content=render_to_string(
        'email/authentication/activate_account.html',
        {
            'code':code
        }
    )
    Email.send_email(
        {
            'subject': "Ro'yxatdan o'tish",
            'to_email': email,
            'body': html_content,
            'content_type': 'html'

        }
    )