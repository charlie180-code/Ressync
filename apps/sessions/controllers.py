from flask import render_template, request, flash, redirect, url_for, jsonify
from . import session
from .. import db
from flask_babel import _
from flask_login import login_required
from ..decorators import school_it_admin_required
from ..models.general.company import Company
from ..models.school.session import Session
from ..models.school.academic_year import AcademicYear
from datetime import datetime
from ..models.school.student import Student
from ..models.school.classroom import Class
from ..models.school.teacher import Teacher
from flask_babel import gettext as _

@session.route("/manage_sessions/<int:company_id>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
@school_it_admin_required
def manage_sessions(company_id):
    company = Company.query.get_or_404(company_id)
    year_id = request.args.get('year', type=int)
    page = request.args.get('page', 1, type=int)
    academic_years = AcademicYear.query.filter_by(company_id=company_id).all()

    if request.method == 'POST':
        data = request.get_json(force=True)
        name = data.get('name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        academic_year_id = data.get('academic_year')

        if not name or not start_date or not end_date:
            return jsonify({"success": False, "message": _("Tous les champs sont requis")}), 400

        new_session = Session(
            name=name,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            company_id=company_id,
            academic_year_id=academic_year_id
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify(
            {
                "title": _('Nouvelle session créee'),
                "success": True, 
                "message": _("Session académique créée avec succès!"),
                "confirmButtonText": _("OK")
            }
        )

    elif request.method == 'PUT':
        data = request.form
        updated = []

        for key, value in data.items():
            if key.startswith('name_') or key.startswith('start_date_') or key.startswith('end_date_'):
                try:
                    session_id = int(key.split('_')[1])
                except (IndexError, ValueError):
                    continue  

                field = key.split('_')[0]
                session_obj = Session.query.get(session_id)
                
                if not session_obj:
                    continue
                
                if field == 'name':
                    session_obj.name = value
                elif field == 'start_date':
                    session_obj.start_date = datetime.strptime(value, '%Y-%m-%d').date()
                elif field == 'end_date':
                    session_obj.end_date = datetime.strptime(value, '%Y-%m-%d').date()
                
                updated.append(session_id)

        db.session.commit()
        return jsonify(
            {
                "title": _("Mise à jour effectuée!"),
                "success": True, 
                "message": _("Les informations de la session ont été mises à jour."),
                "updated_ids": updated,
                "confirmButtonText": _('OK')
            }
        )

    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        session_id = data.get('session_id')
        session_obj = Session.query.get_or_404(session_id)

        total_sessions = Session.query.filter_by(company_id=company_id).count()
        if total_sessions == 1:
            return jsonify({
                "title": _("Opération non autorisée"),
                "success": False,
                "message": _("Impossible de supprimer la dernière session."),
                "confirmButtonText": _('OK')
            }), 400

        # Check if there are any students associated with the session
        associated_students = Student.query.filter_by(session_id=session_id).count()
        if associated_students > 0:
            return jsonify({
                "title": _("Opération non autorisée"),
                "success": False,
                "message": _("Des étudiants sont associés à cette session, impossible de la supprimer."),
                "confirmButtonText": _('OK')
            }), 400

        # Proceed with deletion if checks pass
        db.session.delete(session_obj)
        db.session.commit()
        return jsonify({
            "title": _("Supprimée"),
            "success": True, 
            "message": _("Session supprimée!"),
            "confirmButtonText": _('OK')
        })


    else:
        if year_id:
            academic_year = AcademicYear.query.get_or_404(year_id)
            sessions = Session.query.filter_by(company_id=company_id, academic_year_id=year_id).all()
            inactive_sessions = Session.query.filter_by(
                company_id=company_id,
                academic_year_id=year_id,
                active=False
            ).all()
        else:
            sessions = Session.query.filter_by(company_id=company_id).all()
            inactive_sessions = Session.query.filter_by(
                company_id=company_id,
                active=False
            ).all()
        

        academic_years = AcademicYear.query.filter_by(company_id=company_id).all()

        return render_template(
            'dashboard/@support_team/school/manage_session.html',
            company=company,
            sessions=sessions,
            academic_years=academic_years,
            inactive_sessions=inactive_sessions
        )


@session.route("/manage_academic_years/<int:company_id>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
@school_it_admin_required
def manage_academic_years(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'GET':
        academic_years = AcademicYear.query.filter_by(company_id=company_id).all()
        return render_template(
            'dashboard/@support_team/school/manage_academic_year.html',
            company=company,
            academic_years=academic_years
        )

    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        tuition_fees = data.get('tuition_fees')
        currency = data.get('currency')
        
        if not name or not start_date or not end_date or not tuition_fees or not currency:
            return jsonify({"success": False, "message": _("Tous les champs sont requis.")})

        new_year = AcademicYear(
            company_id=company_id,
            name=name,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            tuition_fees=tuition_fees,
            currency=currency
        )
        db.session.add(new_year)
        db.session.commit()
        return jsonify(
            {
                "title": _('Nouvelle année ajoutée!'),
                "success": True, 
                "message": _( "Année académique créée avec succès!"),
                "confirmButtonText": _('OK')
            }
        )

    elif request.method == 'PUT':
        data = request.form
        updated = []

        for key, value in data.items():
            if key.startswith('name_') or key.startswith('start_date_') or key.startswith('end_date_') or key.startswith('currency_') or key.startswith('tuition_fees_'):
                try:
                    session_id = int(key.split('_')[1])
                except (IndexError, ValueError):
                    continue  

                field = key.split('_')[0]
                session_obj = Session.query.get(session_id)
                
                if not session_obj:
                    continue
                
                if field == 'name':
                    session_obj.name = value
                elif field == 'start_date':
                    session_obj.start_date = datetime.strptime(value, '%Y-%m-%d').date()
                elif field == 'end_date':
                    session_obj.end_date = datetime.strptime(value, '%Y-%m-%d').date()
                elif field == 'currency':
                    session_obj.currency = value
                elif field == 'tuition_fees':
                    session_obj.tuition_fees = value
                
                updated.append(session_id)

        db.session.commit()
        return jsonify(
            {
                "success": True, 
                "updated_ids": updated,
                "message": _('Les modifications ont été sauvegardées.')
            }
        )
    
    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        year_id = data.get('year_id')
        year = AcademicYear.query.get_or_404(year_id)
        
        if not year:
            return jsonify({"success": False, "message": "Année académique non trouvée."})

        db.session.delete(year)
        db.session.commit()
        return jsonify({"success": True, "message": "Année académique supprimée avec succès!"})

    return jsonify({"success": False, "message": "Méthode non autorisée."})


@session.route('/update-session-status/<int:session_id>', methods=['PUT'])
@school_it_admin_required
@login_required
def update_session_status(session_id):
    """a
    This operation updates the session's active status.
    """
    data = request.json
    active = data.get('active')

    session = Session.query.get_or_404(session_id)
    session.active = True

    try:
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@session.route('/migrate-to-a-new-session/<int:session_id>', methods=['PUT'])
@school_it_admin_required
@login_required
def migrate_session(session_id):
    """
    This operation will change the session ID for each student, class, and teacher.
    """
    data = request.json
    new_session_id = data.get('new_session_id')

    if not new_session_id:
        return jsonify({'success': False, 'error': 'New session ID is required'}), 400

    session = Session.query.get_or_404(session_id)
    new_session = Session.query.get_or_404(new_session_id)

    if new_session:
        new_session.active = True

    # Fetch the company ID from the current session
    company_id = session.company_id

    try:
        students_to_update = Student.query.filter_by(session_id=session.id, company_id=company_id).all()
        for student in students_to_update:
            student.session_id = new_session.id

        classes_to_update = Class.query.filter_by(session_id=session.id, company_id=company_id).all()
        for cls in classes_to_update:
            cls.session_id = new_session.id

        teachers_to_update = Teacher.query.filter_by(session_id=session.id, company_id=company_id).all()
        for teacher in teachers_to_update:
            teacher.session_id = new_session.id

        session.active = False

        db.session.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500





