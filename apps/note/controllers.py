from flask import render_template, request, jsonify, abort
from flask_login import login_required, current_user
from ..models.general.note import Note
from ..models.general.company import Company
from ..models.general.user import User
from ..models.general.role import Role
from .emails.note_informer import informer
from . import note
from .. import db
from flask_babel import gettext as _

@note.route("/notes/create_notice/<int:company_id>", methods=["GET", "POST"])
@login_required
def add_notes(company_id):
    company = Company.query.get_or_404(company_id)
    
    if not (current_user.is_responsible() or current_user.is_school_admin()):
        abort(403)
    
    if request.method == "POST":
        title = request.form.get('title')
        nature = request.form.get('nature')
        content = request.form.get('content')
        
        new_note = Note(
            title=title,
            content=content,
            nature=nature,
            company_id=company.id
        )
        db.session.add(new_note)
        db.session.commit()

        # Roles that should not receive the email
        excluded_roles = ['User', 'Reseller', 'Student', 'Parent']

        # Query all users in the company except those with excluded roles
        users_to_notify = User.query.join(Role).filter(
            User.company_id == company.id,
            ~Role.name.in_(excluded_roles)
        ).all()

        # Send email notifications
        for user in users_to_notify:
            informer(
                company_name=company.title,
                email=user.email,
                title=title,
                nature=nature,
                content=content
            )

        return jsonify(
            {
                'title': _('Note ajoutée!'),
                'message': _('Note ajoutée avec succès'),
                'success': True,
                'confirmButtonText': _('OK')
            }
        )

    return render_template('api/@support_team/notice/create_notice.html', company=company)

@note.route("/notes/previous_notes/<int:company_id>")
@login_required
def previous_notes(company_id):
    company = Company.query.get_or_404(company_id)
    
    if not (current_user.is_responsible() or current_user.is_school_admin()):
        abort(403)

    previous_notes = Note.query.filter_by(company_id=company.id).all()
    return render_template(
        "dashboard/@support_team/previous_notes.html",
        previous_notes=previous_notes,
        company=company
    )

@note.route("/manage/note/<int:note_id>", methods=["GET", "POST", "DELETE", "PUT"])
@login_required
def manage_note(note_id):
    note = Note.query.get_or_404(note_id)

    if not (current_user.is_responsible() or current_user.is_school_admin()):
        abort(403)

    if request.method == 'GET':
        return jsonify({'success': True, 'note': {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'nature': note.nature
        }})
    if request.method == 'PUT':
        data = request.get_json(force=True)
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.nature = data.get('nature', note.nature)
        db.session.commit()
        return jsonify(
            {
                'title': _('Note mise à jour'),
                'success': True,
                'message': _('La note a été mise à jour'),
                'confirmButtonText': _('OK')
            }
        )

    if request.method == 'DELETE':
        db.session.delete(note)
        db.session.commit()
        return jsonify(
            {
                'title': _('Note supprimée'),
                'success': True,
                'message': _('La note a été supprimée')
            }
            
        )