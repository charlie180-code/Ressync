from flask import render_template
from flask_mail import Message
from flask_babel import gettext as _
from ... import mail
from dotenv import load_dotenv
import os

load_dotenv()

def notify_new_event(company_name, email, event_title, start_from, end_at):
    subject = _("Nouvel évèvnement: ") + event_title
    html_body = render_template(
        'emails/company/new_event.html', 
        event_title=event_title, 
        company_name=company_name,
        start_from=start_from,
        end_at=end_at,
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
