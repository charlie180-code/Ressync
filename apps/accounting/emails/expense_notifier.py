from flask import render_template
from flask_mail import Message
from flask_babel import gettext as _
from ... import mail
from dotenv import load_dotenv
import os

load_dotenv()


def notify_ceo(ceo_email, company_name, amount, category, currency):
    subject = _("Nouvelle facture depuis ") + company_name
    html_body = render_template(
        'emails/school/expense_report.html', 
        email=ceo_email,
        amount=amount,
        currency=currency,
        category=category,
        login_url=os.environ.get('LOGIN_URL')
    )    
    msg = Message(
        subject, 
        recipients=[ceo_email], 
        html=html_body, 
        sender=os.environ.get('MAIL_DEFAULT_SENDER')
    )
    try:
        mail.send(msg)
        print(f"Email sent successfully to {ceo_email}")
    
    except Exception as e:
        print(f"Failed to send email to {ceo_email}: {str(e)}")
