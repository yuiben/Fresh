import email
from django.core.mail import EmailMessage
import os
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags



def send_email_to_user(to_email:str,user_data:dict):
    subject='Forgot Password'
    email_template_path = os.path.join('email', 'user_forgot_password.html')
    html_message = render_to_string(email_template_path,context=user_data)
    plain_message = strip_tags(html_message)
    from_email = os.environ.get('EMAIL_FROM')
    mail.send_mail(subject,plain_message,from_email,[to_email],html_message=html_message)
