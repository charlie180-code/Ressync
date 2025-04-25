from flask import render_template, request, jsonify
from . import section
from flask_login import login_required
from ..decorators import school_it_admin_required
from ..models.general.company import Company
from ..models.school.section import Section
from datetime import datetime
from flask_babel import gettext as _
from .. import db


@section.route("/manage_sections/<int:company_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@school_it_admin_required
def manage_sections(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        data = request.get_json(force=True)
        name = data.get('name')
        created_at = data.get('created_at_date')
        
        existing_section = Section.query.filter_by(name=name, company_id=company_id).first()
        if existing_section:
            return jsonify({
                'success': False,
                'message': _('Une section du même nom existe déjà'),
                'title': _('Erreur'),
                'confirmButtonText': _('Ok')
            }), 400

        new_section = Section(
            name=name,
            created_at=datetime.strptime(created_at, '%Y-%m-%d'),
            company_id=company_id,
            classes=[]
        )
        db.session.add(new_section)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': _('Nouvelle section créée'),
            'title': _('Section créée'),
            'confirmButtonText': _('Ok')
        }), 201

    elif request.method == 'PUT':
        updated_sections = request.json

        for section in updated_sections:
            section_id = section['id']
            new_name = section['name']
            new_created_at_str = section['created_at']

            try:
                new_created_at = datetime.strptime(new_created_at_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'title': _('Erreur de format de date'),
                    'message': _('Le format de la date est incorrect'),
                    'confirmButtonText': _('OK')
                }), 400

            section_to_update = Section.query.filter_by(id=section_id).first()
            if section_to_update:
                section_to_update.name = new_name
                section_to_update.created_at = new_created_at

        db.session.commit()

        return jsonify({
            'success': True,
            'title': _('Mise à jour effectuée'),
            'message': _('Les sections ont été mises à jour'),
            'confirmButtonText': _('OK')
        }), 200
    
    elif request.method == 'DELETE':
        data = request.get_json()
        section_id = data.get('sectionId')

        section = Section.query.filter_by(id=section_id, company_id=company_id).first_or_404()

        other_sections = Section.query.filter_by(company_id=company_id).count()

        if other_sections <= 1:
            return jsonify({
                'success': False,
                'message': _('Vous ne pouvez pas supprimer la seule dernière session'),
                'title': _('Erreur!'),
                'confirmButtonText': _('Ok')
            }), 400

        if section.classes:
            return jsonify({
                'success': False,
                'message': _('Vous ne pouvez pas supprimer cette session, parceque des classes ou filières lui sont associées'),
                'title': _('Erreur!'),
                'confirmButtonText': _('Ok')
            }), 400

        db.session.delete(section)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': _('Section supprimée'),
            'title': _('Suppression effectuée'),
            'confirmButtonText': _('Ok')
        }), 200

    sections = Section.query.filter_by(company_id=company.id).all()
    return render_template(
        'dashboard/@support_team/school/manage_section.html',
        company=company,
        sections=sections
    )
