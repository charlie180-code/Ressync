from flask import render_template, jsonify, request, redirect, url_for, flash, abort
import os
from . import user
from flask_login import login_required, current_user
from newsdataapi import NewsDataApiClient
from .support_team.business.insights import (
    get_weekly_financial_summary, get_monthly_user_summary, 
    get_daily_client_summary, get_user_invoices, count_all_students,
    calculate_student_count_percentage_difference, calculate_student_data_size,
    count_school_sessions, get_academic_year_for_session, get_number_of_books,
    get_number_of_book_loans, calculate_total_versed_by_students,
    calculate_total_expenses, count_all_companies, get_daily_company_summary,
    get_data_size_for_company
)
from ..models.shipping.product import Product
from ..models.shipping.purchase import Purchase
from ..models.general.invoice import Invoice
from ..models.general.company import Company
from ..models.general.message import Message
from ..models.general.user import User, generate_password_hash
from ..models.general.role import Role
from ..utils import save_files
from .. import db
from flask_babel import gettext as _
from ..auth.utils import check_internet_connection, save_file_locally
from .utils import fetch_emails
from datetime import datetime

@user.route("/user_home/<int:company_id>")
@login_required
def user_home(company_id):
    company = Company.query.get_or_404(company_id)

    api = NewsDataApiClient(apikey=os.environ.get('NEWS_API_KEYS')) 
    
    student_count = count_all_students(company_id) or 0
    student_count_percentage_difference = calculate_student_count_percentage_difference(company_id) or 0
    student_data_size = calculate_student_data_size(company_id) or 0
    session_count = count_school_sessions(company_id) or 0
    academic_year = get_academic_year_for_session(company_id) or "N/A"
    book_count = get_number_of_books(company_id) or 0
    book_loan_count = get_number_of_book_loans(company_id) or 0
    total_versed = calculate_total_versed_by_students(company_id) or 0
    total_expenses = calculate_total_expenses(company_id) or 0

    summary = get_weekly_financial_summary(company_id) or {}
    user_summary = get_monthly_user_summary(company_id) or {}
    client_summary = get_daily_client_summary(company_id) or {}
    companies = count_all_companies() or 0
    invoices = get_user_invoices(current_user.id) or []
    daily_company_summary = get_daily_company_summary() or {}
    published_products = Product.query.filter_by(user_id=current_user.id).all() or []
    new_products = Product.query.filter_by(company_id=company.id).all() or []
    purchases = Purchase.query.filter_by(user_id=current_user.id).all() or []

    invoices = Invoice.query.filter_by(company_id=company_id).all()    
    expenses = [expense for invoice in invoices for expense in invoice.expenses]



    total_size_mb = get_data_size_for_company(company_id) / (1024 * 1024)  

    

    return render_template(
        "dashboard/user_home.html",
        summary=summary,
        user_summary=user_summary,
        client_summary=client_summary,
        invoices=invoices,
        purchases=purchases,
        published_products=published_products,
        new_products=new_products,
        company=company,
        book_count=book_count,
        book_loan_count=book_loan_count,
        student_count=student_count,
        student_count_percentage_difference=student_count_percentage_difference,
        student_data_size=student_data_size,
        session_count=session_count,
        academic_year=academic_year,
        total_versed=total_versed,
        total_expenses=total_expenses,
        companies=companies,
        daily_company_summary=daily_company_summary,
        total_disk_usage_mb=total_size_mb,
        expenses=expenses
    )


@user.route("/settings/<int:company_id>", methods=['GET', 'POST'])
@login_required
def settings(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        # Get user profile data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        address = request.form.get('address')
        username = request.form.get('username')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        profile_image = request.files.get('profile_image')
        email_provider = request.form.get('email_provider')
        email_username = request.form.get('email_username')
        email_password = request.form.get('email_password')
        email_smtp_server = request.form.get('smtp_server')
        email_smtp_port = request.form.get('smtp_port')
        email_imap_server = request.form.get('imap_server')
        email_imap_port = request.form.get('imap_port')


        # get service mutations data
        transport_company = request.form.get('transport_company')
        arrival_date = request.form.get('arrival_date')
        leaving_date = request.form.get('leaving_date')

        # Get company data
        company_logo = request.files.get('company_logo')
        company_email = request.form.get('company_email')
        company_name = request.form.get('company_name')
        company_address = request.form.get('company_address')
        company_phone = request.form.get('company_phone')
        company_website = request.form.get('company_website')

        if not email:
            flash(_("L'adresse email est requise"), "error")
            return redirect(url_for('user.settings', company_id=company.id))

        if new_password and new_password != confirm_password:
            flash(_("Le nouveau mot de passe et la confirmation ne correspondent pas."), "error")
            return redirect(url_for('user.settings', company_id=company.id))

        # Update user profile
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.address = address
        current_user.username = username

        current_user.email_provider = email_provider
        current_user.email_username = email_username
        current_user.email_password = email_password
        current_user.imap_port = email_imap_port
        current_user.smtp_server = email_smtp_server
        current_user.smtp_port = email_smtp_port
        current_user.imap_server = email_imap_server
        

        current_user.transport_company = transport_company

        if arrival_date:
            arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            current_user.arrival_date = arrival_date
        else:
            current_user.arrival_date = None
        if leaving_date:
            leaving_date = datetime.strptime(leaving_date, "%Y-%m-%d").date()
            current_user.leaving_date = leaving_date

        else:
            current_user.leaving_date = None


        # Handle profile image upload
        if profile_image:
            if profile_image.mimetype.startswith('image/'):
                if profile_image.content_length > 5 * 1024 * 1024:
                    flash(_("La taille de l'image ne doit pas dépasser 5 Mo."), "error")
                    return redirect(url_for('user.settings', company_id=company.id))
                try:
                    if check_internet_connection():
                        # Save the profile image remotely
                        saved_profile_image_url = save_files([profile_image], "user_profile_pictures")[0]
                    else:
                        save_result = save_file_locally(profile_image, folder_name="user_profile_pictures")
                        saved_profile_image_url = url_for('auth.local_files',
                            folder='user_profile_pictures',
                            filename=os.path.basename(save_result["absolute_path"]),
                            _external=True)

                    current_user.profile_picture_url = saved_profile_image_url
                except Exception as e:
                    flash(_(f"Échec de l'enregistrement de l'image de profil: {str(e)}"), "error")
                    return redirect(url_for('user.settings', company_id=company.id))
            else:
                flash(_("Fichier image non valide."), "error")
                return redirect(url_for('user.settings', company_id=company.id))

        # Handle password change
        if old_password and new_password:
            if current_user.verify_password(old_password):
                current_user.password_hash = generate_password_hash(new_password)
            else:
                flash(_("L'ancien mot de passe est incorrect."), "error")
                return redirect(url_for('user.settings', company_id=company.id))

        # Handle company logo upload
        if company_logo:
            if company_logo.mimetype.startswith('image/'):
                if company_logo.content_length > 5 * 1024 * 1024:
                    flash(_("La taille de l'image ne doit pas dépasser 5 Mo."), "error")
                    return redirect(url_for('user.settings', company_id=company.id))
                try:
                    if check_internet_connection():
                        saved_company_logo_url = save_files([company_logo], "company_logos")[0]
                    else:
                        save_result = save_file_locally(company_logo, folder_name="company_logos")
                        saved_company_logo_url = url_for('auth.local_files',
                            folder='company_logos',
                            filename=os.path.basename(save_result["absolute_path"]),
                            _external=True)

                    company.logo_url = saved_company_logo_url
                except Exception as e:
                    flash(_(f"Échec de l'enregistrement du logo de la société: {str(e)}"), "error")
                    return redirect(url_for('user.settings', company_id=company.id))
            else:
                flash(_("Fichier image non valide."), "error")
                return redirect(url_for('user.settings', company_id=company.id))

        if company_email:
            company.email = company_email
        if company_name:
            company.title = company_name
        if company_address:
            company.location = company_address
        if company_phone: 
            company.phone_number = company_phone
        if company_website: 
            company.website_url = company_website

        db.session.commit()
        flash(_("Profil mis à jour avec succès."), "success")
        return redirect(url_for('user.settings', company_id=company.id))

    return render_template(
        "dashboard/settings.html",
        company=company
    )




# for students
@user.route('/friends/<int:company_id>')
@login_required
def friends(company_id):
    company = Company.query.get_or_404(company_id)

    if current_user.company_id != company.id:
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = 10

    students_query = User.query.filter_by(company_id=company.id).join(Role).filter(Role.name == 'Student')
    pagination = students_query.paginate(page=page, per_page=per_page, error_out=False)

    students = pagination.items
    total_pages = pagination.pages

    student_data = []
    for student in students:
        if student.id == current_user.id:
            continue

        friends_in_common = current_user.friends_in_common(student)

        student_data.append({
            'first_name': student.first_name,
            'last_name': student.last_name,
            'profile_picture_url': student.profile_picture_url,
            'friends_in_common': friends_in_common,
        })

    return render_template(
        "views/school/student/my_friends.html",
        company=company,
        students=student_data,
        page=page,
        total_pages=total_pages
    )

@user.route('/chats/<int:company_id>')
@login_required
def chats(company_id):
    company = Company.qery.get_or_404(company_id)
    return render_template(
        'views/school/student/chats.html',
        company_id=company.id
    )



