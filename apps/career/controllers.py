from flask import render_template, request, jsonify, flash, redirect, url_for, abort, current_app, send_file
from datetime import datetime
from flask_login import login_required, current_user
from . import career
from ..models.general.jobapplication import JobApplication
from ..models.general.user import User
from ..models.general.role import Role
from ..models.general.employee import Employee
from ..models.general.company import Company
from ..models.general.file import File
from ..models.engineering.pipeline import Pipeline
import os
from .. import db
from ..utils import save_files
from flask_babel import _
from ..decorators import school_hr_manager_required, customer_required
from werkzeug.utils import secure_filename
from datetime import datetime
from ..auth.utils import check_internet_connection, save_file_locally
from .utils import generate_excel, generate_pdf, generate_qr_code, save_qr_code_to_static, generate_badge
import json

@career.route("/employees/<int:company_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def employees(company_id):
    company = Company.query.get_or_404(company_id)
    if not current_user.is_responsible():
        abort(403)

    if request.method == 'GET':
        employees = Employee.query.filter_by(company_id=company.id)
        
        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = employees.paginate(page=page, per_page=per_page, error_out=False)
        employees = pagination.items

        return render_template(
            'dashboard/@support_team/employees_listing.html',
            employees=employees,
            pagination=pagination,
            company=company
        )
    
    elif request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email_address = request.form.get('email_address')
        job_title = request.form.get('job_title')
        identifier = request.form.get('identifier')
        wage = float(request.form.get('wage', 0))
        services = request.form.get('services')
        date_of_birth = request.form.get('date_of_birth')

        # Validate required fields
        if not all([first_name, last_name, job_title]):
            return jsonify({'success': False, 'message': 'Tous les champs obligatoires doivent être remplis'}), 400

        # Handle profile picture upload
        picture_url = None
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            if check_internet_connection():
                saved_profile_image_filename = save_files([profile_picture], "user_profile_pictures")[0]
                picture_url = saved_profile_image_filename
            else:
                save_result = save_file_locally(profile_picture, folder_name="user_profile_pictures")
                picture_url = url_for('auth.local_files',
                    folder='user_profile_pictures',
                    filename=os.path.basename(save_result["absolute_path"]),
                    _external=True)

        try:
            new_employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email_address=email_address,
                job_title=job_title,
                identifier=identifier,
                wage=wage,
                services=services,
                date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d') if date_of_birth else None,
                picture_url=picture_url,
                company_id=company_id,
                member_since=datetime.utcnow()
            )
            db.session.add(new_employee)
            db.session.flush()  # To get the employee ID

            # Handle file uploads
            uploaded_files = request.files.getlist('uploaded_files')
            for file in uploaded_files:
                if file:
                    if check_internet_connection():
                        saved_file_filename = save_files([file], f"company_user_files/{company_id}")[0]
                        saved_file_url = saved_file_filename
                    else:
                        save_result = save_file_locally(file, folder_name=f"company_user_files/{company_id}")
                        saved_file_url = url_for('auth.local_files',
                            folder=f'company_user_files/{company_id}',
                            filename=os.path.basename(save_result["absolute_path"]),
                            _external=True)

                    new_file = File(
                        label=file.filename,
                        filepath=saved_file_url,
                        folder_id=None,
                        user_id=new_employee.id,
                        company_id=company_id
                    )
                    db.session.add(new_file)

            db.session.commit()
            return jsonify({
                'title': _('Effectué'),
                'success': True,
                'message': _('Employé créé avec succès')
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
        
    elif request.method == "PUT":
        data = request.form
        employee_id = data.get('employee_id')
        employee = Employee.query.filter_by(id=employee_id, company_id=company_id).first()
        if not employee:
            return jsonify({'error': _('L\'employé n\'existe pas')}), 404

        # For profile picture upload
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            if check_internet_connection():
                saved_profile_image_filename = save_files([profile_picture], "user_profile_pictures")[0]
                saved_profile_image_url = saved_profile_image_filename
            else:
                save_result = save_file_locally(profile_picture, folder_name="user_profile_pictures")
                saved_profile_image_url = url_for('auth.local_files',
                    folder='user_profile_pictures',
                    filename=os.path.basename(save_result["absolute_path"]),
                    _external=True)
            
            employee.picture_url = saved_profile_image_url

        # For general file uploads
        uploaded_files = request.files.getlist('uploaded_files')
        for file in uploaded_files:
            if file:
                if check_internet_connection():
                    saved_file_filename = save_files([file], f"company_user_files/{company_id}")[0]
                    saved_file_url = saved_file_filename
                else:
                    save_result = save_file_locally(file, folder_name=f"company_user_files/{company_id}")
                    saved_file_url = url_for('auth.local_files',
                        folder=f'company_user_files/{company_id}',
                        filename=os.path.basename(save_result["absolute_path"]),
                        _external=True)

                new_file = File(
                    label=file.filename,
                    filepath=saved_file_url,
                    folder_id=None,
                    user_id=employee.id,
                    company_id=company_id
                )
                db.session.add(new_file)

        employee.first_name = data.get('firstName', employee.first_name)
        employee.last_name = data.get('lastName', employee.last_name)
        employee.email_address = data.get('email', employee.email_address)
        employee.job_title = data.get('job_title', employee.job_title)
        employee.identifier = data.get('identifier', employee.identifier)
        employee.wage = float(data.get('wage', employee.wage or 0))
        employee.services = data.get('services', employee.services)
        
        def parse_date(date_str):
            if date_str and isinstance(date_str, str):
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    return None
            return None
        
        employee.date_of_birth = parse_date(data.get('date_of_birth', employee.date_of_birth))

        db.session.commit()
        return jsonify({
            'title': _('Mise à jour effectuée'),
            'message': _('Les informations de l\'employé ont été mises à jour avec succès'),
            'confirmButtonText': _('OK')
        }), 200
    

@career.route('/download_employee_list', methods=['GET'])
@login_required
def download_employee_list():
    company_id = request.args.get('company_id')
    format_type = request.args.get('format', 'pdf')
    pipeline_id = request.args.get('pipeline_id', type=int)
    
    company = Company.query.get_or_404(company_id)
    pipelines = Pipeline.query.filter_by(company_id=company_id).all()

    employees_query = User.query.join(Role).filter(
        User.company_id == company_id,
        ~Role.position.in_(['customer'])
    )

    if pipeline_id:
        employees_query = employees_query.filter(User.pipeline_id == pipeline_id)

    employees_query = employees_query.order_by(User.first_name, User.last_name)

    employees = employees_query.all()

    employee_data = [{
        'id': emp.id,
        'first_name': emp.first_name,
        'last_name': emp.last_name,
        'fonction': emp.role.name,
        'matricule': emp.employee_id if emp.employee_id else ' ',
        'pipeline_name': emp.station.pipeline_name if emp.pipeline_id else 'N/A',
        'address': emp.address if emp.address else ' ',
        'phone_number': emp.phone_number if emp.phone_number else ' ',
        'date_of_birth': emp.date_of_birth.strftime('%Y-%m-%d') if emp.date_of_birth else 'N/A',
        'place_of_birth': emp.place_of_birth if emp.place_of_birth else ' '
    } for emp in employees]

    qr_code_buffer = generate_qr_code(company.website_url or "https://defaultcompany.com")
    qr_code_url = save_qr_code_to_static(qr_code_buffer)

    if format_type == 'pdf':
        return generate_pdf(company, employee_data, qr_code_url)
    elif format_type == 'excel':
        return generate_excel(company, employee_data)
    else:
        return "Invalid format", 400
    