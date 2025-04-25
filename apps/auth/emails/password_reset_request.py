from flask import render_template, url_for, current_app
from flask_mail import Message
from flask_babel import gettext as _
from ... import mail
from dotenv import load_dotenv
import os

load_dotenv()


def send_reset_email(to_email, token):
    reset_url = url_for('auth.reset_with_token', token=token, _external=True)
    
    subject = _("Réinitialiser votre mot de passe")
    
    html_body = render_template(
        'emails/auth/reset_password.html', 
        email=to_email, 
        token=token,
        reset_url=reset_url
    )    
    
    msg = Message(
        subject, 
        recipients=[to_email], 
        html=html_body, 
        body=_("Pour réinitialiser votre mot de passe, veuillez visiter ce lien: {}").format(reset_url),
        sender=os.environ.get('MAIL_DEFAULT_SENDER')
    )
    
    try:
        mail.send(msg)
        print(f"Email sent successfully to {to_email}")
    
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")