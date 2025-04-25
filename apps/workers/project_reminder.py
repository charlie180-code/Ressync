from .. import create_app, mail
from ..models.general.folder import Folder
from ..models.general.user import User
from flask_login import current_user
from flask import render_template, current_app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask_mail import Message
from datetime import timedelta, datetime
from flask_babel import gettext as _

app = create_app()
scheduler = BackgroundScheduler()

def send_project_reminders():
    today = datetime.utcnow().date()
    one_week_later = today + timedelta(days=7)

    with app.app_context():
        projects = Folder.query.filter(
            Folder.deadline <= one_week_later,
            Folder.deadline >= today
        ).all()

        for project in projects:
            days_remaining = (project.deadline - today).days
            if days_remaining <= 7 and days_remaining >= 0:
                users_to_notify = User.query.filter(
                    User.company_id == project.company_id,
                    User.id != current_user.id
                ).all()

                subject = _("Rappel: Le projet '{title}' arrive à échéance bientôt").format(title=project.name)
                html_body = render_template(
                    'emails/company/project_reminder.html',
                    project_title=project.name,
                    deadline=project.deadline,
                    days_remaining=days_remaining,
                    login_url=current_app.config.get('LOGIN_URL')
                )

                for user in users_to_notify:
                    if user.is_sales() or user.is_responsible() or user.is_company_it_administrator() or user.is_agent():
                        msg = Message(
                            subject,
                            recipients=[user.email],
                            html=html_body,
                            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
                        )

                        try:
                            mail.send(msg)
                            print(f"Reminder sent successfully to {user.email}")
                        except Exception as e:
                            print(f"Failed to send reminder to {user.email}: {str(e)}")

def start_scheduler():
    scheduler.add_job(
        send_project_reminders,
        trigger=IntervalTrigger(days=1),
        id='project_reminder_job',
        name='Send project reminders one week before the deadline',
        replace_existing=True
    )

    scheduler.start()

if __name__ == "__main__":
    start_scheduler()
    app.run()
