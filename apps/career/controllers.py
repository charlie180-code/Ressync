from flask import render_template, request, jsonify, flash, redirect, url_for, abort, current_app, send_file
from datetime import datetime
from flask_login import login_required, current_user
from . import career
from ..models.general.jobapplication import JobApplication
from ..models.general.job import Job
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

@career.route("/my-previous-applications/<int:company_id>", methods=['GET'])
@login_required
def my_previous_applications(company_id):
    company = Company.query.get_or_404(company_id)
    user_applications = JobApplication.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'dashboard/applied_jobs_listing.html', 
        user_applications=user_applications,
        company=company
    )

@career.route("/careers/previous_created_jobs/<int:company_id>")
@login_required
def previous_created_jobs(company_id):
    if not(current_user.is_responsible()):
        abort(403)
    company = Company.query.get_or_404(company_id)
    jobs = Job.query.filter_by(company_id=company.id).all()
    return render_template(
        "dashboard/@support_team/previous_created_jobs.html",
        jobs=jobs,
        company=company
    )


@career.route("/careers/recent_applications/<int:company_id>", methods=['GET'])
@login_required
def recent_applications(company_id):
    if not(current_user.is_responsible()):
        abort(403)
    company = Company.query.get_or_404(company_id)
    jobs = Job.query.filter_by(company_id=company.id).all()
    selected_job_id = request.args.get('job_id')
    applications = []

    if selected_job_id:
        selected_job = Job.query.get_or_404(selected_job_id)
        if selected_job:
            applications = JobApplication.query.filter_by(job_id=selected_job_id).order_by(JobApplication.apply_at.desc()).all()

    return render_template(
        'dashboard/@support_team/applicants_list.html',
        jobs=jobs, 
        applications=applications, 
        selected_job_id=selected_job_id, 
        company=company
    )

@career.route("/careers/employees_table/<int:company_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def employee_table(company_id):
    company = Company.query.get_or_404(company_id)
    if not current_user.is_responsible():
        abort(403)

    if request.method == 'GET':
        pipeline_id = request.args.get('pipeline_id', type=int)

        pipelines = Pipeline.query.filter_by(company_id=company_id).all()

        employees_query = User.query.join(Role).filter(
            User.company_id == company_id,
            ~Role.position.in_(['customer'])
        )

        if pipeline_id:
            employees_query = employees_query.filter(User.pipeline_id == pipeline_id)

        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = employees_query.paginate(page=page, per_page=per_page, error_out=False)
        employees = pagination.items

        return render_template(
            'dashboard/@support_team/employees_listing.html',
            employees=employees,
            pagination=pagination,
            pipelines=pipelines,
            selected_pipeline=pipeline_id,
            company=company
        )
    
    elif request.method == "PUT":
        data = request.form
        employee_id = data.get('employee_id')
        employee = User.query.filter_by(id=employee_id, company_id=company_id).first()
        if not employee:
            return jsonify({'error': _('L\'employé n\'existe pas')}), 404

        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            company_folder = 'user_profile_pictures'
            local_folder = os.path.join(current_app.root_path, 'static', company_folder)
            
            if not os.path.exists(local_folder):
                os.makedirs(local_folder)
            
            if check_internet_connection():
                saved_profile_image_filename = save_files([profile_picture], company_folder)[0]
                saved_profile_image_url = saved_profile_image_filename
            else:
                saved_profile_image_filename = save_file_locally(profile_picture, local_folder)
                saved_profile_image_url = url_for('static', filename=f"{company_folder}/{saved_profile_image_filename}", _external=True)
            
            employee.profile_picture_url = saved_profile_image_url

        uploaded_files = request.files.getlist('uploaded_files')
        company_user_files_folder = f"company_user_files/{company_id}/"
        local_files_folder = os.path.join(current_app.root_path, 'static', company_user_files_folder)

        if not os.path.exists(local_files_folder):
            os.makedirs(local_files_folder)

        for file in uploaded_files:
            if file:
                if check_internet_connection():
                    saved_file_filename = save_files([file], company_user_files_folder)[0]
                    saved_file_url = saved_file_filename
                else:
                    saved_file_filename = save_file_locally(file, local_files_folder)
                    saved_file_url = url_for('static', filename=f"{company_user_files_folder}/{saved_file_filename}", _external=True)

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
        employee.role.name = data.get('role', employee.role.name)
        employee.registration_number = data.get('registration_number', employee.registration_number)
        employee.social_security_number = data.get('social_security', employee.social_security_number)
        employee.service_name = data.get('service_name', employee.service_name)
        employee.emergency_contact_phone = data.get('emergency_contact', employee.emergency_contact_phone)
        employee.certifications = data.get('certifications', employee.certifications)
        employee.bank_name = data.get('bank_name', employee.bank_name)
        employee.bank_account_number = data.get('bank_account_number', employee.bank_account_number)

        if company.category in ['Education', 'Shipping', 'Engeneering']:
            arrival_date = data.get('arrival_date', None)
            leaving_date = data.get('leaving_date', None)

            if arrival_date:
                try:
                    employee.arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Invalid format for arrival_date. Expected 'YYYY-MM-DD'.")

            if leaving_date:
                try:
                    employee.leaving_date = datetime.strptime(leaving_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Invalid format for leaving_date. Expected 'YYYY-MM-DD'.")

            employee.transport_company = data.get('transport_company', employee.transport_company)

        def parse_date(date_str):
            if date_str and isinstance(date_str, str):
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    return None
            return None
        
        employee.contract_start_date = parse_date(data.get('contract_start_date', employee.contract_start_date))
        employee.contract_end_date = parse_date(data.get('contract_end_date', employee.contract_end_date))
        employee.employment_terms = data.get('employment_terms', employee.employment_terms)
        employee.address = data.get('address', employee.address)

        employee.gender = data.get('gender', employee.gender)
        employee.email = data.get('email', employee.email)
        employee.place_of_birth = data.get('place_of_birth', employee.place_of_birth)

        employee.date_of_birth = parse_date(data.get('date_of_birth', employee.date_of_birth))

        employee.contract_start_date = employee.contract_start_date if isinstance(employee.contract_start_date, datetime) else None
        employee.contract_end_date = employee.contract_end_date if isinstance(employee.contract_end_date, datetime) else None
        employee.date_of_birth = employee.date_of_birth if isinstance(employee.date_of_birth, datetime) else None
        employee.current_location = data.get('current_location', employee.current_location)

        db.session.commit()
        return jsonify({
            'title': _('Mise à jour effectuée'),
            'message': _('Les informations de l\'employé ont été mises à jour avec succès'),
            'confirmButtonText': _('OK')
        }), 200

@career.route("/careers/add_a_job/<int:company_id>", methods=["GET", "POST"])
@login_required
def create_job(company_id):
    if not(current_user.is_responsible):
        abort(403)
    company = Company.query.get_or_404(company_id)
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
        except Exception as e:
            return jsonify({"success": False, "message": "Invalid JSON payload"}), 400

        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        salary = data.get('salary')
        posted_date_str = data.get('posted_date')
        closing_date_str = data.get('closing_date')
        
        errors = []
        if not title:
            errors.append( _("Le titre est requis.") )
        if not description:
            errors.append( _("La description est requise."))
        if not location:
            errors.append( _("Le lieu est requis."))
        if not salary:
            errors.append( _("Le salaire est requis."))
        if not posted_date_str:
            errors.append( _("La date de publication est requise."))
        if not closing_date_str:
            errors.append( _("La date de clôture est requise."))
        
        if errors:
            return jsonify(
                {
                    "title": _("Erreur"),
                    "success": False, 
                    "message": " ".join(errors),
                    "confirmButtonText": _('OK')
                }
            ), 400
        
        try:
            posted_date = datetime.strptime(posted_date_str, '%Y-%m-%d')
            closing_date = datetime.strptime(closing_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify(
                {
                    'title': _('Erreur'),
                    "success": False, 
                    "message": _("Dates invalides."),
                    "confirmButtonText": _('OK')
                }
            ), 400
        
        job = Job(
            title=title,
            description=description,
            location=location,
            salary=salary,
            posted_date=posted_date,
            closing_date=closing_date,
            company_id=company.id
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify(
            {
                "success": True, 
                "title" : "Offre d\'emploi",
                "message": "Offre d'emploi créée avec succès!",
                "confirmButtonText": _('OK')
            }
        ), 200
    
    return render_template('api/@support_team/jobs/create_job.html', company=company)



@career.route("/careers/edit_job/<int:job_id>/<int:company_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id, company_id):
    if not(current_user.is_responsible()):
        abort(403)
    job = Job.query.get_or_404(job_id)
    company = Company.query.get_or_404(company_id)
    if request.method == "POST":
        job.title = request.form['title']
        job.description = request.form['description']
        job.location = request.form['location']
        job.salary = request.form['salary']
        job.posted_date = datetime.strptime(request.form['posted_date'], '%Y-%m-%d')
        job.closing_date = datetime.strptime(request.form['closing_date'], '%Y-%m-%d')
        job.company_id = company.id
        db.session.commit()
        return redirect(url_for('career.previous_created_jobs', company_id=company.id))
    return render_template('api/@support_team/jobs/edit_job.html', job=job, company=company)

@career.route("/careers/delete_job/<int:job_id>/<int:company_id>", methods=["DELETE"])
@login_required
def delete_job(job_id, company_id):
    if not(current_user.is_responsible()):
        abort(403)
    job = Job.query.get_or_404(job_id)
    company = Company.query.get_or_404(company_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'success' : True})
    


@career.route("/careers/employees/delete_employee/<int:employee_id>", methods=["DELETE"])
@login_required
def delete_employee(employee_id):
    if not(current_user.is_responsible()):
        abort(403)
    employee = Employee.query.get_or_404(employee_id)
    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@career.route("/careers/submit_application/<int:job_id>", methods=["POST"])
@login_required
def submit_application(job_id):
    job = Job.query.get_or_404(job_id)
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    location = request.form['location']
    motivation = request.form['motivation']
    linkedin = request.form['linkedin']
    github = request.form['github']
    dribble = request.form['dribble']
    date_of_birth = request.form['date_of_birth']
    cv = request.files['cv']
    
    cv_url = f"/static/uploads/{cv.filename}"
    cv.save(f"app/static/uploads/{cv.filename}")

    application = JobApplication(
        applicant_first_name=first_name,
        applicant_last_name=last_name,
        applicant_email_address=email,
        applicant_location=location,
        motivation=motivation,
        linkedin_url=linkedin,
        github_url=github,
        dribble_url=dribble,
        date_of_birth=date_of_birth,
        CV_url=cv_url,
        user_id=current_user.id,
        job_id=job.id
    )
    db.session.add(application)
    db.session.commit()

    return redirect(url_for('main.my_recent_applications'))


@career.route("/job-openings/apply/<int:job_id>/<int:company_id>", methods=['GET', 'POST'])
@login_required
@customer_required
def apply_job(job_id, company_id):
    job = Job.query.get_or_404(job_id)
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            motivation = request.form['motivation']
            linkedin = request.form.get('linkedin', '')
            github = request.form.get('github', '')
            dribble = request.form.get('dribble', '')
            date_of_birth = request.form.get('date_of_birth')
            address = request.form['address']
            cv = request.files.get('cv')
            
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d') if date_of_birth else None
            
            if cv:
                cv_url = save_files([cv], 'cvs')[0]
            else:
                cv_url = None

            job_application = JobApplication(
                applicant_first_name=first_name,
                applicant_last_name=last_name,
                applicant_email_address=email,
                applicant_location=address,
                motivation=motivation,
                linkedin_url=linkedin,
                github_url=github,
                dribble_url=dribble,
                date_of_birth=date_of_birth,
                CV_url=cv_url,
                user_id=current_user.id,
                job_id=job.id
            )
            
            db.session.add(job_application)
            db.session.commit()
            
            return jsonify({'message': _('Votre dossier a été soumis!')}), 200
        
        except Exception as e:
            return jsonify({'message': _('Une erreur s\'est produite lors de la soumission')}), 500

    return render_template(
        'api/customers/jobs/apply.html',
        job=job,
        company=company
    )


@career.route("/careers/job_list/<int:company_id>")
@login_required
def job_list(company_id):
    if not(current_user.is_responsible()):
        abort(403)
    company = Company.query.get_or_404(company_id)
    jobs = Job.query.filter_by(company_id=company.id).all()
    return render_template('api/@support_team/jobs/job_list.html', jobs=jobs, company=company)


@career.route("/careers/new_jobs/<int:company_id>")
@login_required
def new_jobs(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template("dashboard/jobs_listing.html", company=company)


@career.route("/manage_recruitment/<int:company_id>")
@login_required
@school_hr_manager_required
def manage_recruitment(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template(
        'dashboard/@support_team/school/manage_recruitment.html',
        company=company
    )


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
    
@career.route('/generate_employee_badge', methods=['POST'])
def generate_employee_badge():
    try:
        data = request.get_json()
        user_id = data.get('employee_id')
        company_id = data.get('company_id')

        if not user_id or not company_id:
            return jsonify({"error": "User ID and Company ID are required"}), 400

        user = User.query.get_or_404(user_id)
        company = Company.query.get_or_404(company_id)

        pdf_buffer = generate_badge(user, company)
        
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, as_attachment=True, download_name="employee_badge.pdf", mimetype='application/pdf')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
