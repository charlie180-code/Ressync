from flask import render_template
from flask_mail import Message
from flask_babel import gettext as _
from .... import mail
from dotenv import load_dotenv
import os

load_dotenv()


def welcome_company(email, password):
    subject = _("Bienvenue sur notre plateforme")
    
    html_body = render_template(
        'emails/company/welcome.html', 
        email=email, 
        password=password,
        login_url=os.environ.get('LOGIN_URL')
    )

    msg = Message(
        subject, 
        recipients=[email], 
        html=html_body, 
        sender=os.environ.get('MAIL_DEFAULT_SENDER')
    )
    
    try:
        mail.send(msg)
        print(f"Email sent successfully to {email}")
    
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
