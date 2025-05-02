from flask import render_template, request, jsonify, flash, redirect, url_for, flash, session, current_app, send_file, abort, send_from_directory
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash
from . import auth
import re
from ..models.general.user import User, generate_password_hash
from ..models.general.company import Company
from ..models.general.role import Role
from ..models.utils import roles_translations
from ..models.school.session import Session
from ..models.school.classroom import Class
from ..models.school.student import Student
from ..models.school.subject import Subject
from ..models.school.teacher import Teacher
from ..models.school.installment import Installment
from ..models.school.exam import Exam
from ..models.school.academic_year import AcademicYear
from ..models.school.subject_teacher import subject_teacher
from ..models.school.parent import Parent
from ..models.general.file import File
from ..models.engineering.pipeline import Pipeline
from sqlalchemy.sql import insert
from ..models.school.class_subject import class_subject
from datetime import datetime, timedelta
from flask_babel import _
from flask_login import login_user, logout_user
import os
from dotenv import load_dotenv
from .utils import generate_invoice, confirm_reset_token, generate_reset_token, check_internet_connection, save_file_locally, get_company_files, get_resource_path
from .. import oauth, db
from ..utils import save_files
from .emails.company.welcome import welcome_company
from .emails.school.school_admin_welcome import welcome_school_admin, welcome_school_teacher
from .emails.school.student_welcome import welcome_new_student, welcome_student_parent
from ..utils import generate_password
from ..decorators import school_it_admin_required, it_administrator_required
from .emails.password_reset_request import send_reset_email
from werkzeug.utils import secure_filename
from .session import store_session_token, get_session_token, clear_session_token
import json

load_dotenv()


google = oauth.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
    consumer_secret=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email',
        'prompt': 'consent'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_data = request.get_json(force=True)
        email = login_data.get('email')
        password = login_data.get('password')
        remember_me = login_data.get('remember_me', False)

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'success': False, 'errorType': 'incorrectEmail'}), 401

        if not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'errorType': 'incorrectPassword'}), 401

        company_id = user.company_id
        login_user(user, remember=remember_me)
        
        if remember_me:
            token = user.get_remember_token()
            expiry = datetime.utcnow() + timedelta(days=30)
            
            
            user.remember_token = token
            user.remember_token_expiry = expiry
            db.session.commit()
            
            token_data = {
                'token': token,
                'expiry': expiry.isoformat(),
                'company_id': company_id,
                'email': email,
                'user_id': user.id
            }
            
            store_session_token(token_data)
            
            stored_token = get_session_token()

            response = jsonify({
                'success': True, 
                'company_id': company_id,
                'remember_token': token
            })
            response.set_cookie(
                'remember_token',
                value=token,
                max_age=30*24*60*60,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            return response
        else:
            if company_id:
                return jsonify({'success': True, 'company_id': company_id})
            return jsonify({'success': True})

    return render_template('auth/login.html')


@auth.route('/auth/token-login', methods=['POST'])
def token_login():
    token_data = request.get_json()
    if not token_data or 'token' not in token_data:
        return jsonify({'authenticated': False}), 400
    
    # First verify against database
    user = User.verify_remember_token(token_data['token'])
    if not user or (user.remember_token_expiry and user.remember_token_expiry < datetime.utcnow()):
        return jsonify({'authenticated': False}), 401
    
    # Then verify against session file
    session_data = get_session_token()
    if not session_data or session_data.get('token') != token_data['token']:
        return jsonify({'authenticated': False}), 401
    
    login_user(user)
    return jsonify({
        'authenticated': True,
        'company_id': user.company_id,
        'user_id': user.id
    })

@auth.before_app_request
def load_user_from_remember_token():
    if current_user.is_authenticated:
        return
    
    remember_token = request.cookies.get('remember_token')
    if remember_token:
        user = User.verify_remember_token(remember_token)
        if user and user.remember_token_expiry > datetime.utcnow():
            login_user(user)
            return
    
    session_data = get_session_token()
    if session_data:
        user = User.verify_remember_token(session_data['token'])
        if user and datetime.fromisoformat(session_data['expiry']) > datetime.utcnow():
            login_user(user)


@auth.route('/status', methods=['GET'])
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'company_id': current_user.company_id,
            'remember_token': request.cookies.get('remember_token')
        })
    else:
        remember_token = request.cookies.get('remember_token')
        if remember_token:
            user = User.verify_remember_token(remember_token)
            if user and user.remember_token_expiry > datetime.utcnow():
                login_user(user)
                return jsonify({
                    'authenticated': True,
                    'company_id': user.company_id,
                    'remember_token': remember_token
                })
        return jsonify({'authenticated': False})
    


@auth.route('/google_login_authorized')
def google_authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        flash('Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(url_for('auth.login'))

    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')

    email = user_info.data['email']

    user = User.query.filter_by(email=email).first()

    if not user:
        flash( _('Veuillez créer un compte pour continuer'), 'error')
        return redirect(url_for('auth.signup'))

    login_user(user)

    return redirect(url_for('main.user_home'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@auth.route('/google_login')
def google_login():
    return google.authorize(callback=url_for('auth.google_authorized', _external=True))


@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        SignUpData = request.get_json(force=True)

        first_name = SignUpData.get('firstName')
        last_name = SignUpData.get('lastName')
        email = SignUpData.get('email')
        password = SignUpData.get('password')
        confirm_password = SignUpData.get('confirmPassword')
        tools = SignUpData.get('tools', [])
        field = SignUpData.get('field')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'email_exists'})

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'password_mismatch'})

        if len(password) < 8:
            return jsonify({'success': False, 'message': 'weak_password'})

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            tools=json.dumps(tools),
            field_of_study=field
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True})

    return render_template("auth/signup.html")


@auth.route('/google_signup')
def google_signup():
    return google.authorize(callback=url_for('auth.google_signup_authorized', _external=True))

@auth.route('/google_signup_authorized')
def google_signup_authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        flash('Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(url_for('auth.signup'))

    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')

    email = user_info.data['email']
    name = user_info.data.get('name', 'User')

    user = User.query.filter_by(email=email).first()
    if user:
        flash( _('Ce compte existe déja, veuillez vous connecter'), 'error')
        return redirect(url_for('auth.login'))

    new_user = User(
        email=email, 
        first_name=name,
        last_name=name, 
        password=generate_password_hash(os.urandom(24).hex())
    )

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return redirect(url_for('main.user_home'))

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Basic validation
        if not email:
            flash(_('Veuillez entrer votre adresse e-mail.'), 'danger')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash(_('Veuillez entrer une adresse e-mail valide.'), 'danger')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                token = generate_reset_token(user)
                send_reset_email(user.email, token)
                flash(_('Un email contenant des instructions a été envoyé à {}').format(user.email), 'success')
            else:
                flash(_('Aucun compte n\'est associé à {}').format(email), 'danger')
        
        return redirect(url_for('auth.reset_password'))
    
    return render_template('auth/reset_password_request.html')

@auth.route("/reset/<token>", methods=['GET', 'POST'])
def reset_with_token(token):
    user_id = confirm_reset_token(token)

    if request.method == 'POST':
        if user_id:
            user = User.query.get(user_id)
        else:
            flash(_('Le lien de réinitialisation est invalide ou a expiré'), 'danger')
            return redirect(url_for('auth.reset_password'))
        
        confirm_password = request.form.get('confirm_password')
        password = request.form.get('password')
        if not password:
            flash(_('Votre mot de passe est requis pour continuer'), 'danger')
            return redirect(url_for('auth.reset_with_token', token=token))
        
        elif not confirm_password:
            flash(_('Veuillez confirmer votre mot de passe pour continuer'), 'danger')
            return redirect(url_for('auth.reset_with_token', token=token))

        elif not (password==confirm_password):
            flash(_('Les deux mots de passe ne correspondent pas'), 'danger')
            return redirect(url_for('auth.reset_with_token', token=token))
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash(_('Votre mot de passe a été réinitialisé, veuillez vous connecter'), 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/new_password.html')


@auth.route("/reset_email", methods=['GET', 'POST'])
def reset_email():
    if request.method == 'POST':
        print('This is a post request')
    return render_template("auth/reset_email.html")


@auth.route('/logout')
def logout():
    clear_session_token()
    logout_user()
    response = redirect(url_for('auth.login'))
    response.delete_cookie('remember_token')
    return response

@auth.route("/company/register", methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        category = request.form.get('category')
        nature = request.form.get('nature')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        website_url = request.form.get('website_url')
        linkedin_url = request.form.get('linkedin_url')
        twitter_url = request.form.get('twitter_url')
        facebook_url = request.form.get('facebook_url')
        number_of_employees = request.form.get('number_of_employees')
        year_established = request.form.get('year_established')
        annual_revenue = request.form.get('annual_revenue')

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        logo_file = request.files.get('logo')

        if not title:
            return jsonify({"error": "Company title is required"}), 400
        if not logo_file:
            return jsonify({"error": "Logo file is required"}), 400
        
        
        if check_internet_connection():
            saved_logo_url = save_files([logo_file], "company_logos")[0]
        else:
            save_result = save_file_locally(logo_file, folder_name="company_logos")
    
            saved_logo_url = url_for('auth.local_files', 
                folder='company_logos',
                filename=os.path.basename(save_result["absolute_path"]),
                _external=True)



        company = Company(
            title=title,
            description=description,
            logo_url=saved_logo_url,
            location=location,
            category=category,
            nature=nature,
            email=email,
            phone_number=phone_number,
            website_url=website_url,
            linkedin_url=linkedin_url,
            twitter_url=twitter_url,
            facebook_url=facebook_url,
            number_of_employees=number_of_employees,
            year_established=year_established,
            annual_revenue=annual_revenue
        )

        db.session.add(company)
        db.session.commit()


        new_it_admin = User(
            email=email,
            password_hash=generate_password_hash(password),
            company_id=company.id
        )

        if company.category == 'Education':
            it_admin_role = Role.query.filter_by(name='School IT Administrator').first()
            if it_admin_role:
                new_it_admin.role = it_admin_role
        
        elif company.category == 'Other':
            admin_role = Role.query.filter_by(name='HR Manager').first()
            if admin_role:
                new_it_admin.role = admin_role

        else:
            it_admin_role = Role.query.filter_by(name='IT Administrator').first()
            if it_admin_role:
                new_it_admin.role = it_admin_role

        db.session.add(new_it_admin)
        db.session.commit()

        if check_internet_connection():
            welcome_company(email, password)

        return jsonify({"message": "Company registered successfully!"}), 200
    
    return render_template("auth/register_company.html")


@auth.route('/local_files/<folder>/<filename>')
def local_files(folder, filename):
    base_dir = get_resource_path(folder)
    return send_from_directory(base_dir, filename)


# for school admins
@auth.route("/manage_admins/<int:company_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@school_it_admin_required
def manage_admins(company_id):
    if request.method == 'GET':
        company = Company.query.get_or_404(company_id)
        admins = User.query.join(Role).filter(
            User.company_id == company_id,
            Role.name.in_(['School Admin', 'School Accountant', 'Librarian'])
        ).all()

        roles = Role.query.filter(Role.name.in_([
            'School Admin', 
            'School Accountant', 
            'Librarian',
            'School IT Administrator'
        ])).all()

        return render_template(
            'auth/school/@support_team/it_admin/admin/manage_admin.html',
            company=company,
            admins=admins,
            roles=roles
        )
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        role_id = data.get('role_id')
        password = generate_password()

        if not name or not email or not role_id:
            return jsonify(
                {
                    "title": _('Erreur'),
                    "error": _('Infos incomplètes'),
                    'confirmButtonText': _('OK')
                }
            ), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify(
                {
                    "title": _('Erreur'),
                    "error": _("Cette adresse e-mail existe déjà!"),
                    'confirmButtonText': _('OK')
                }
            ), 400
        
        new_user = User(
            first_name=name,
            email=email,
            password_hash=generate_password_hash(password),
            company_id=company_id
        )

        role = Role.query.get(role_id)
        role_name = roles_translations.get(role.name, role.name)

        db.session.add(new_user)
        db.session.commit()

        new_user.role_id = role.id
        db.session.commit()

        if check_internet_connection():
            welcome_school_admin(email, password, role_name)

        return jsonify(
            {
                "title": _('Nouvel administrateur ajouté!'),
                "message": _('Le nouvel administrateur a été ajouté!'),
                "confirmButtonText": _('OK')
            }
        ), 201

    elif request.method == 'PUT':
        data = request.get_json()
        user_id = data.get('user_id')
        name = data.get('name')
        email = data.get('email')
        role_id = data.get('role_id')

        if not user_id or not name or not email or not role_id:
            return jsonify(
                {
                    "title": _('Infos incomplètes'),
                    "error": _('Infos incomplètes'),
                    "confirmButtonText": _('OK')
                }
            ), 400

        user = User.query.get_or_404(user_id)
        user.first_name = name
        user.email = email
        user.role_id = role_id

        role = Role.query.get(role_id)
        role_name = roles_translations.get(role.name, role.name)

        db.session.commit()

        return jsonify(
            {
                "title": _('Mise à jour effectuée'),
                "message": _('Infos mises à jour!'),
                "confirmButtonText": _('OK')
            }
        ), 200

    elif request.method == 'DELETE':
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify(
                {
                    "error": _('id de l\'utilisateur introuvable')
                }
            ), 400

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return jsonify(
            {
                "title": _('Supprimé!'),
                "message": _('Administrateur supprimé!'),
                'confirmButtonText': _('OK')
            }
        ), 200


@auth.route("/manage_students/<int:company_id>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
@school_it_admin_required
def manage_students(company_id):
    company = Company.query.get_or_404(company_id)
    academic_year_id = request.args.get('academic_year_id', type=int) 
    
    if request.method == "POST":
        data = request.json
        try:
            student_email = data['email']
            
            # Check if the email already exists
            existing_user = User.query.filter_by(email=student_email).first()
            if existing_user:
                return jsonify(error="Cette adresse e-mail existe déjà"), 400
            
            student_password = generate_password()
            student_user = User(
                first_name=data['firstName'],
                last_name=data['lastName'],
                gender=data['gender'],
                email=student_email,
                date_of_birth=datetime.strptime(data['dateOfBirth'], '%Y-%m-%d'),
                place_of_birth=data['placeOfBirth'],
                password_hash=generate_password_hash(student_password),
                company_id=company_id,
            )
            db.session.add(student_user)
            db.session.commit()

            # Create student and assign to class and session
            student = Student(
                user_id=student_user.id,
                class_id=data['classId'],
                session_id=data['sessionId'],
                company_id=company_id
            )
            db.session.add(student)
            db.session.commit()

            # Assign subjects and exams to the new student
            class_id = data['classId']
            subjects = Subject.query.join(class_subject).filter(class_subject.c.class_id == class_id).all()
            exams = Exam.query.filter_by(class_id=class_id).all()

            student.subjects = subjects
            student.exams = exams

            db.session.commit()

            # Assign student role
            student_role = Role.query.filter_by(name='Student').first()
            if student_role:
                student_user.role_id = student_role.id
                db.session.commit()
                role_name = student_role.name
                if check_internet_connection():
                    welcome_new_student(student_email, student_password, role_name)

            # Creating parent and handling first installment
            parent_email = data.get('parentEmail')
            if parent_email:
                existing_parent_user = User.query.filter_by(email=parent_email).first()

                if existing_parent_user:
                    parent_user = existing_parent_user
                else:
                    # Generate a password for the parent
                    parent_password = generate_password()
                    parent_user = User(
                        first_name=data['parentFirstName'],
                        last_name=data['parentLastName'],
                        email=parent_email,
                        password_hash=generate_password_hash(parent_password),
                        company_id=company_id,
                    )
                    db.session.add(parent_user)
                    db.session.commit()

                    # Assign parent role
                    parent_role = Role.query.filter_by(name='Parent').first()
                    if parent_role:
                        parent_user.role_id = parent_role.id
                        db.session.commit()

                    if check_internet_connection():
                        welcome_student_parent(parent_email, parent_password, parent_role.name)
                
                # Create the parent record in the Parent table
                parent = Parent(
                    user_id=parent_user.id
                )
                db.session.add(parent)
                db.session.commit()

                # Link parent to student
                student.parent_id = parent.id
                db.session.commit()

            # Handle first installment
            if data.get('firstInstallment'):
                installment = Installment(
                    amount=data['firstInstallment'],
                    due_date=datetime.utcnow(),
                    class_id=data['classId'],
                    student_id=student.id,
                    currency=data['currency'],
                    is_paid=False
                )
                db.session.add(installment)
                db.session.commit()

            invoice_pdf_response = generate_invoice(student.id)
            
            return invoice_pdf_response


        except Exception as e:
            db.session.rollback()
            return jsonify(
                error=str(e), 
                confirmButtonText=_('OK')
            ), 500

    elif request.method == "PUT":
        data = request.form

        try:
            student_id = data.get('student_id')
            user_id = data.get('user_id') 
            company_id = data.get('company_id')

            student = Student.query.filter_by(id=student_id, company_id=company_id).first()

            if not student:
                return jsonify({'error': _('L\'étudiant n\'existe pas')}), 404

            student_user = student.user
            student_user.first_name = data.get('firstName', student_user.first_name)
            student_user.last_name = data.get('lastName', student_user.last_name)
            student_user.gender = data.get('gender', student_user.gender)
            student_user.email = data.get('email', student_user.email)
            student_user.place_of_birth = data.get('placeOfBirth', student_user.place_of_birth)

            if 'dateOfBirth' in data:
                student_user.date_of_birth = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d')

            # Update student's class if provided
            if 'classId' in data:
                student.class_id = data['classId']
                # Reassign subjects and exams for the new class
                new_class_id = data['classId']
                student.subjects = Subject.query.join(class_subject).filter(class_subject.c.class_id == new_class_id).all()
                student.exams = Exam.query.filter_by(class_id=new_class_id).all()

            # Handle profile picture upload
            if 'profile_picture' in request.files:
                profile_picture = request.files['profile_picture']
                if profile_picture:
                    company_folder = 'user_profile_pictures'
                    local_folder = os.path.join(current_app.root_path, 'static', company_folder)

                    if not os.path.exists(local_folder):
                        os.makedirs(local_folder)

                    # Check internet connection
                    if check_internet_connection():
                        profile_picture_path = save_files([profile_picture], company_folder)[0]
                        student_user.profile_picture_url = profile_picture_path
                    else:
                        # Save locally
                        profile_picture_path = os.path.join(local_folder, secure_filename(profile_picture.filename))
                        profile_picture.save(profile_picture_path)
                        student_user.profile_picture_url = f"{company_folder}/{secure_filename(profile_picture.filename)}"

            # Handle uploaded files
            if 'uploaded_file' in request.files:
                files = request.files.getlist('uploaded_file')  # Get all uploaded files

                for file in files:
                    if file:
                        company_user_files_folder = f"company_user_files/{company_id}/"
                        local_files_folder = os.path.join(current_app.root_path, 'static', company_user_files_folder)

                        if not os.path.exists(local_files_folder):
                            os.makedirs(local_files_folder)

                        # Check internet connection
                        if check_internet_connection():
                            uploaded_file_url = save_files([file], company_user_files_folder)[0]
                        else:
                            # Save locally
                            file_path = os.path.join(local_files_folder, secure_filename(file.filename))
                            file.save(file_path)
                            uploaded_file_url = f"{company_user_files_folder}/{secure_filename(file.filename)}"

                        # Create and save the new file entry
                        new_file = File(
                            label=file.filename,
                            filepath=uploaded_file_url,
                            folder_id=student.class_id,
                            user_id=user_id,
                            company_id=company_id
                        )
                        db.session.add(new_file)

            db.session.commit()

            invoice_pdf_response = generate_invoice(student.id)
            
            return invoice_pdf_response


        except Exception as e:
            db.session.rollback()
            return jsonify(error=str(e), title=_('Erreur'), confirmButtonText=_('OK')), 500


    elif request.method == "DELETE":
        data = request.get_json(force=True)
        try:
            student_id = data.get('student_id')
            student = Student.query.get_or_404(student_id)
            user = student.user
            installments = Installment.query.filter_by(student_id=student.id).all()
            for installment in installments:
                db.session.delete(installment)

            db.session.delete(student)

            db.session.delete(user)

            db.session.commit()
            return jsonify(
                message=_('L\'élève a bien été supprimé'), 
                title=_('Supprimé'), 
                confirmButtonText=_('OK')
            ), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify(
                {
                    "title": _('Erreur'),
                    "confirmButtonText": _('OK'),
                    "error": str(e)
                }
            ), 400

    page = request.args.get('page', 1, type=int)
    session_id = request.args.get('session_id', type=int)
    class_id = request.args.get('class_id', type=int)

    sessions = Session.query.filter_by(company_id=company_id).all()
    classes = Class.query.filter_by(company_id=company_id).all()
    
    """
    here check all the files connected at the same time to the
    user and also check files that contains the company_id
    cause user can use the cloud for his personal usage...
    he can store his movies, music for working etc.. with 5GB also 
    he can also use it to import his work on Adobe Photoshop, 
    Illustrator, Gimp, Inkscape
    """

    class_dict = {cls.id: cls.name for cls in classes}
    session_dict = {session.id: session.name for session in sessions}

    academic_years = AcademicYear.query.filter_by(company_id=company_id).all()

    students_query = Student.query.join(User).filter(Student.company_id == company.id)

    if session_id and class_id and academic_year_id:
        students_query = students_query.join(Class).join(Session).filter(
            Class.id == class_id,
            Class.session_id == session_id,
            Session.academic_year_id == academic_year_id
        )
    elif session_id and academic_year_id:
        students_query = students_query.join(Class).join(Session).filter(
            Class.session_id == session_id,
            Session.academic_year_id == academic_year_id
        )


    elif session_id and class_id:
        students_query = students_query.join(Class).filter(Class.id == class_id, Class.session_id == session_id)
    elif session_id:
        students_query = students_query.join(Class).filter(Class.session_id == session_id)
    elif class_id:
        students_query = students_query.filter_by(class_id=class_id)

    students_query = students_query.order_by(User.first_name, User.last_name)
    pagination = students_query.paginate(page=page, per_page=10, error_out=False)
    students = pagination.items

    return render_template(
        'auth/school/@support_team/it_admin/student/manage_student.html',
        company=company,
        company_id=company.id,
        sessions=sessions,
        academic_years=academic_years,
        classes=classes,
        class_dict=class_dict,
        students=students,
        pagination=pagination,
        selected_session=session_id,
        selected_class=class_id,
        session_dict=session_dict,
        selected_academic_year=academic_year_id
    )


@auth.route("/manage_teachers/<int:company_id>", methods=['POST', 'DELETE', 'PUT', 'GET'])
@login_required
@school_it_admin_required
def manage_teachers(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        session_id = data.get('session_id')
        wage = data.get('wage')
        wage_system = data.get('wage_system')
        currency = data.get('currency')

        if not first_name or not last_name or not email or not session_id:
            return jsonify(message=_("Tous les champs sont obligatoires.")), 400
        
        password = generate_password()

        user = User(
            first_name=first_name, 
            last_name=last_name, 
            email=email,
            password_hash=generate_password_hash(password),
            company_id=company.id
        )
        db.session.add(user)
        db.session.flush()

        role = Role.query.filter_by(name='Teacher').first()
        user.role_id = role.id
        role_name = role.name
        
        teacher = Teacher(
            user_id=user.id, 
            company_id=company.id, 
            session_id=session_id,
            wage=wage,
            wage_system=wage_system,
            currency=currency
        )
        db.session.add(teacher)
        db.session.commit()

        if check_internet_connection():
            welcome_school_teacher(email, password, role_name)
        
        return jsonify(message=_("Enseignant ajouté avec succès.")), 201
        
    elif request.method == 'PUT':
        data = request.get_json()
        teacher_id = data.get('teacher_id')
        teacher = Teacher.query.get_or_404(teacher_id)
        teacher.user.first_name = data.get('first_name', teacher.user.first_name)
        teacher.user.last_name = data.get('last_name', teacher.user.last_name)
        teacher.user.email = data.get('email', teacher.user.email)
        teacher.session_id = data.get('session_id', teacher.session_id)
        teacher.wage = data.get('wage', teacher.wage)
        teacher.wage_system = data.get('wage_system', teacher.wage_system)
        teacher.currency = data.get('currency', teacher.currency)
    
        db.session.commit()
        
        return jsonify(message=_("Enseignant mis à jour avec succès.")), 200

    elif request.method == 'DELETE':
        data = request.get_json()
        teacher_id = data.get('teacher_id')
        teacher = Teacher.query.get_or_404(teacher_id)
        db.session.delete(teacher)
        db.session.commit()
        
        return jsonify(message=_("Enseignant supprimé avec succès.", confirmButtonText=_('OK'))), 200
    
    else:
        # Get current page from query parameter (default to 1)
        page = request.args.get('page', 1, type=int)
        
        # Get subject and session filters from query parameters
        selected_subject_id = request.args.get('subject_id', type=int)
        selected_session_id = request.args.get('session_id', type=int)

        # Query subjects for dropdown
        subjects = Subject.query.all()

        # Query active academic year for the school
        active_academic_year = AcademicYear.query.filter_by(company_id=company.id, active=1).first()
        if active_academic_year:
            # Query sessions tied to the active academic year
            sessions = Session.query.filter_by(academic_year_id=active_academic_year.id).all()
        else:
            sessions = []

        # Filter teachers based on company and optional subject and session
        query = Teacher.query.join(User).filter(Teacher.company_id == company.id)
        if selected_subject_id:
            query = query.join(subject_teacher).filter(subject_teacher.c.subject_id == selected_subject_id)
        if selected_session_id:
            query = query.filter(Teacher.session_id == selected_session_id)

        # Sort teachers alphabetically by User's first name and last name
        query = query.order_by(User.first_name, User.last_name)

        # Paginate the teachers query
        pagination = query.paginate(page=page, per_page=10, error_out=False)
        teachers = pagination.items

        return render_template(
            'auth/school/@support_team/it_admin/teacher/manage_teacher.html', 
            teachers=teachers, 
            subjects=subjects, 
            sessions=sessions, 
            selected_subject_id=selected_subject_id, 
            selected_session_id=selected_session_id,
            pagination=pagination,
            company=company
        )


@auth.route("/company/register_success")
def company_register_success():
    email = request.args.get('email')
    return render_template('auth/register_company_success.html', email=email)


@auth.route("/manage_company_admins/<int:company_id>", methods=['GET', 'PUT', 'DELETE', 'POST'])
@it_administrator_required
def manage_company_admins(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = User.query.join(Role).filter(
            User.company_id == company_id,
            Role.position.in_(['responsible', 'Sales Manager', 'agent'])
        ).paginate(page=page, per_page=per_page)


        roles = Role.query.filter(Role.position.in_([
            'responsible',
            'Sales Manager',
            'agent'
        ])).all()

        if company.category == 'Engineering':
            pipelines = Pipeline.query.filter_by(company_id=company_id).all()
            return render_template(
                'auth/general/@support_team/it_admin/admin/manage_admin.html',
                company=company,
                admins=pagination.items,
                pagination=pagination,
                roles=roles,
                pipelines=pipelines
            )

        return render_template(
            'auth/general/@support_team/it_admin/admin/manage_admin.html',
            company=company,
            admins=pagination.items,
            pagination=pagination,
            roles=roles
        )
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        role_id = data.get('role_id')
        password = generate_password()
        station = data.get('station')
        
        if not name or not email or not role_id:
            return jsonify(
                {
                    "title": _('Erreur'),
                    "error": _('Infos incomplètes'),
                    'confirmButtonText': _('OK')
                }
            ), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify(
                {
                    "title": _('Erreur'),
                    "error": _("Cette adresse e-mail existe déja!"),
                    'confirmButtonText': _('OK')
                }
            ), 400

        
        new_user = User(
            first_name=name,
            email=email,
            password_hash=generate_password_hash(password),
            company_id=company_id,
            pipeline_id=station
        )
        

        role = Role.query.get(role_id)
        role_name = roles_translations.get(role.name, role.name)

        db.session.add(new_user)
        db.session.commit()

        new_user.role_id = role.id
        db.session.commit()

        if check_internet_connection():
            welcome_school_admin(email, password, role_name)

        return jsonify(
            {
                "title": _('Nouvel agent ajouté!'),
                "message": _('Le nouvel agent a été ajouté!'),
                "confirmButtonText": _('OK')
            }
        ), 201

    elif request.method == 'PUT':
        data = request.get_json()
        user_id = data.get('user_id')
        name = data.get('name')
        email = data.get('email')
        role_id = data.get('role_id')

        if not user_id or not name or not email or not role_id:
            return jsonify(
                {
                    "title": _('Infos incomplètes'),
                    "error": _('Infos incomplètes'),
                    "confirmButtonText": _('OK')
                }
            ), 400

        user = User.query.get_or_404(user_id)
        user.first_name = name
        user.email = email
        user.role_id = role_id

        role = Role.query.get(role_id)
        role_name = roles_translations.get(role.name, role.name)

        db.session.commit()

        return jsonify(
            {
                "title": _('Mise à jour effectuée'),
                "message": _('Infos mises à jour!'),
                "confirmButtonText": _('OK')
            }
        ), 200

    elif request.method == 'DELETE':
        data = request.get_json()
        user_id = data.get('user_id')
        print(user_id)

        if not user_id:
            return jsonify(
                {
                    "error": _('id de l\'utilisateur introuvable')
                }
            ), 400

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return jsonify(
            {
                "title": _('Supprimé!'),
                "message": _('Agent supprimé!'),
                'confirmButtonText': _('OK')
            }
        ), 200
