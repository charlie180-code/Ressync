from flask import render_template, jsonify, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from ..models.general.event import Event
from ..models.general.company import Company
from ..models.general.role import Role
from ..models.general.user import User
from .emails.event_notifier import notify_new_event
from . import calendar
from datetime import datetime
from .. import db


@calendar.route("/events/company/<int:company_id>", methods=['GET', 'POST'])
@login_required
def company_events(company_id):
    if not any([
        current_user.is_responsible(),
        current_user.is_school_admin(),
        current_user.is_agent(),
        current_user.is_sales(),
        current_user.is_company_it_administrator()
    ]):
        abort(403)

    company = Company.query.get_or_404(company_id)
    return render_template("dashboard/@support_team/calendar.html", company=company)

@calendar.route("/events/calendar/<int:company_id>", methods=['GET', 'POST'])
@login_required
def events_calendar(company_id):
    company = Company.query.get_or_404(company_id)

    # Allow access only a head or school admin
    if current_user.is_responsible() or current_user.is_school_admin():
        return render_template("dashboard/@support_team/events.html", company=company)
    
    abort(403)


@calendar.route("/get_events/<int:company_id>", methods=['GET'])
@login_required
def get_events(company_id):
    company = Company.query.get_or_404(company_id)
    events = Event.query.filter_by(company_id=company.id).all()
    events_list = []
    for event in events:
        events_list.append({
            'title': event.title,
            'start': event.start_from.isoformat(),
            'end': event.end_at.isoformat(),
        })
    return jsonify(events_list)



@calendar.route("/add_event/<int:company_id>", methods=['POST'])
@login_required
def add_event(company_id):
    company = Company.query.get_or_404(company_id)
    company_name = company.title

    # Check if the current user is either a responsible or a School Admin
    if not (current_user.is_responsible() or current_user.is_school_admin()):
        return abort(403)
    
    title = request.form.get('title')
    status = request.form.get('status')
    start_from = request.form.get('start_from')
    end_at = request.form.get('end_at')
    report = request.form.get('report')

    try:
        start_from = datetime.fromisoformat(start_from)
        end_at = datetime.fromisoformat(end_at)
    except ValueError as e:
        return redirect(url_for('main.events'))

    new_event = Event(
        title=title,
        status=status,
        start_from=start_from,
        end_at=end_at,
        report=report,
        company_id=company.id
    )

    db.session.add(new_event)
    db.session.commit()

    # Roles that should not receive the email
    excluded_roles = ['User', 'Reseller', 'Student', 'Parent']

    # Query all users in the company except those with excluded roles
    users_to_notify = User.query.join(Role).filter(
        User.company_id == company.id,
        ~Role.name.in_(excluded_roles)
    ).all()

    for user in users_to_notify:
        notify_new_event(
            company_name=company_name,
            email=user.email, 
            event_title=title, 
            start_from=start_from, 
            end_at=end_at
        )

    return redirect(url_for('calendar.events_calendar', company_id=company.id))
