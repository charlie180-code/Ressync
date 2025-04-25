from flask import render_template
from flask_mail import Message
from flask_babel import gettext as _
from ... import mail
from dotenv import load_dotenv
import os

load_dotenv()

def informer(company_name, email, title, nature, content):
    subject = "[" + nature + "]" + _(" Note d\'information ") + company_name
    html_body = render_template(
        'emails/company/new_note.html', 
        email=email, 
        company_name=company_name,
        title=title,
        content=content,
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
