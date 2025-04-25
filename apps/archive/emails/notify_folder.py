from flask import render_template, current_app
from flask_mail import Message
from flask_babel import gettext as _
from ... import mail
from ...models.general.user import User
from dotenv import load_dotenv
from flask_login import current_user
import os

load_dotenv()

def notify_for_new_folder(company_name, folder_name, deadline, company_id):
    if current_user.first_name and current_user.last_name:
        creator_name = f"{current_user.first_name} {current_user.last_name}"
    elif current_user.first_name:
        creator_name = current_user.first_name
    elif current_user.last_name:
        creator_name = current_user.last_name
    else:
        creator_name = current_user.email

    subject = _(f"{company_name} - Nouveau projet: {folder_name}")
    users_to_notify = User.query.filter(
        User.company_id == company_id,
        User.id != current_user.id
    ).all()

    for user in users_to_notify:
        if user.is_customer():
            continue
        
        if user.is_sales() or user.is_responsible() or user.is_company_it_administrator() or user.is_agent():
            html_body = render_template(
                'emails/company/new_folder.html',
                folder_name=folder_name,
                company_name=company_name,
                deadline=deadline,
                login_url=os.environ.get('LOGIN_URL'),
                creator_name=creator_name
            )

            msg = Message(
                subject,
                recipients=[user.email],
                html=html_body,
                sender=os.environ.get('MAIL_DEFAULT_SENDER')
            )

            try:
                mail.send(msg)
                print(f"Email sent successfully to {user.email}")

            except Exception as e:
                print(f"Failed to send email to {user.email}: {str(e)}")


def notify_for_deleted_folder(company_name, folder_name, folder_id, company_id):
    if current_user.first_name and current_user.last_name:
        creator_name = f"{current_user.first_name} {current_user.last_name}"
    elif current_user.first_name:
        creator_name = current_user.first_name
    elif current_user.last_name:
        creator_name = current_user.last_name
    else:
        creator_name = current_user.email

    subject = _(f"{company_name} - Dossier supprimé: {folder_name}")
    users_to_notify = User.query.filter(
        User.company_id == company_id,
        User.id != current_user.id
    ).all()

    for user in users_to_notify:
        if user.is_customer():
            continue
        
        if user.is_sales() or user.is_responsible() or user.is_company_it_administrator() or user.is_agent():
            html_body = render_template(
                'emails/company/deleted_folder.html',
                folder_name=folder_name,
                company_name=company_name,
                folder_id=folder_id,
                creator_name=creator_name
            )

            msg = Message(
                subject,
                recipients=[user.email],
                html=html_body,
                sender=os.environ.get('MAIL_DEFAULT_SENDER')
            )

            try:
                mail.send(msg)
                print(f"Email sent successfully to {user.email}")

            except Exception as e:
                print(f"Failed to send email to {user.email}: {str(e)}")


def notify_users_about_new_files(company, folder, files, labels):
    if current_user.first_name and current_user.last_name:
        creator_name = f"{current_user.first_name} {current_user.last_name}"
    elif current_user.first_name:
        creator_name = current_user.first_name
    elif current_user.last_name:
        creator_name = current_user.last_name
    else:
        creator_name = current_user.email
    subject = _(f"Nouvelle(s) fichier(s) ajoutée(s) au dossier {folder.name} de {company.title}")
    users_to_notify = User.query.filter(
        User.company_id == company.id,
        User.id != current_user.id
    ).all()

    for user in users_to_notify:
        if user.is_customer():
            continue

        if user.is_sales() or user.is_responsible() or user.is_company_it_administrator() or user.is_agent():
            html_body = render_template(
                'emails/company/files_attached.html',
                folder_name=folder.name,
                company_name=company.title,
                files=dict(zip(labels, files)),
                creator_name=creator_name,
                login_url=os.environ.get('LOGIN_URL')
            )

            msg = Message(
                subject,
                recipients=[user.email],
                html=html_body,
                sender=os.environ.get('MAIL_DEFAULT_SENDER')
            )

            try:
                mail.send(msg)
                print(f"Email sent successfully to {user.email}")

            except Exception as e:
                print(f"Failed to send email to {user.email}: {str(e)}")

