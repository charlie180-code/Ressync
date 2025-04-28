from flask import render_template, jsonify, request, redirect, flash, url_for, abort
from flask_login import login_required, current_user
from . import accounting
from ..decorators import school_accountant_required
from ..models.general.invoice import Invoice
from ..models.general.company_expense import CompanyExpense
from ..models.general.company import Company
from ..models.school.student import Student
from ..models.school.academic_year import AcademicYear
from ..models.school.installment import Installment
from ..models.school.classroom import Class
from ..models.school.session import Session
from ..models.general.user import User
from ..models.general.wage import Wage
from ..models.general.role import Role
from ..models.school.expense import Expense
from ..models.general.folder import Folder
from math import ceil
from sqlalchemy import func
from datetime import datetime
from .emails.expense_notifier import notify_ceo
from .. import db
from flask_babel import gettext as _
from .utils import generate_company_invoice
import json
from flask import send_file
import os

@accounting.route("/invoices/<int:company_id>", methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_invoices(company_id):
    if request.method == 'GET':
        if not any([
            current_user.is_responsible(),
            current_user.is_school_admin(),
            current_user.is_agent(),
            current_user.is_sales(),
            current_user.is_company_it_administrator(),
            current_user.is_consultant(),
            current_user.is_administrator()
        ]):
            abort(403)

        company = Company.query.get_or_404(company_id)
        invoices = Invoice.query.filter_by(company_id=company.id).all()

        return render_template("dashboard/@support_team/invoices.html", invoices=invoices, company=company)

    elif request.method == 'POST':
        data = request.get_json()

        client_name = data.get('client_name', '')
        client_type = data.get('client_type', '')
        client_phone = data.get('client_phone', '')
        client_email = data.get('client_email', '')
        client_address = data.get('client_address', '')
        client_city = data.get('client_city', '')
        client_postal_code = data.get('client_postal_code', '')
        client_country = data.get('client_country', '')


        invoice = Invoice(
            company_id=company_id,
            client_name=client_name,
            client_type=client_type,
            client_phone=client_phone,
            client_email=client_email,
            client_address=client_address,
            client_city=client_city,
            client_postal_code=client_postal_code,
            client_country=client_country
        )

        if data.get('attach_to_project'):
            project_id = data.get('project_id')
            if project_id:
                project = Folder.query.get(project_id)
                if project:
                    invoice.project_id = project_id
        
        db.session.add(invoice)
        db.session.commit()

        expenses = data.get('expenses', {})

        for _, expense in expenses.items():
            service_type = expense.get('service_type', '')
            unit_price = float(expense.get('unit_price', '0') or '0')
            quantity = int(expense.get('quantity', '0') or '0')
            currency = expense.get('currency', '')
            details = {
                'storage': expense.get('storage', ''),
                'time of usage': expense.get('time_of_usage', ''),
                'compute power': expense.get('compute_power', ''),
                'bandwidth': expense.get('bandwidth', ''),
                'api calls': expense.get('api_calls', ''),
                'licensing costs': expense.get('licensing_costs', ''),
                'support': expense.get('support', ''),
                'additional costs': expense.get('additional_costs', ''),
                'network type': expense.get('network_type', ''),
                'latency': expense.get('latency', ''),
                'uptime': expense.get('uptime', ''),
                'data transfer costs': expense.get('data_transfer_costs', ''),
                'number of connections': expense.get('number_of_connections', ''),
                'sla': expense.get('sla', ''),
                'support level': expense.get('support_level', ''),
                'product specs': expense.get('product_specs', ''),
                'dimensions': expense.get('dimensions', ''),
                'category': expense.get('category', ''),
                'brand': expense.get('brand', ''),
                'model': expense.get('model', ''),
                'data storage': expense.get('data_storage', ''),
                'data transfer': expense.get('data_transfer', ''),
                'model type': expense.get('model_type', ''),
                'training time': expense.get('training_time', ''),
                'inference time': expense.get('inference_time', ''),
                'license costs': expense.get('license_costs', '')
            }

            expense_record = CompanyExpense(
                service_type=service_type,
                unit_price=unit_price,
                currency=currency,
                quantity=quantity,
                details=details,
                invoice_id=invoice.id
            )
            db.session.add(expense_record)

        db.session.commit()

        return generate_company_invoice(invoice_id=invoice.id)

    elif request.method == 'DELETE':
        data = request.get_json()
        invoice_id = data.get('invoice_id')
        try:
            invoice = Invoice.query.options(
                db.joinedload(Invoice.expenses)
                .get_or_404(invoice_id))

            if invoice.project_id:
                project = Folder.query.get(invoice.project_id)
                if project:
                    # Optionally add back the invoice amount to project budget
                    # project.budget += invoice.total_amount
                    db.session.add(project)

            for expense in invoice.expenses:
                db.session.delete(expense)

            db.session.delete(invoice)
            db.session.commit()

            return jsonify({
                'success': True,
                'title': _('Facture supprimée'),
                'message': _('La facture a été supprimée')
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'title': _('Erreur'),
                'message': _('Une erreur est survenue lors de la suppression: ') + str(e)
            }), 500

        




@accounting.route("/manage_student_fees/<int:company_id>")
@login_required
@school_accountant_required
def manage_student_fees(company_id):
    company = Company.query.get_or_404(company_id)
    page = int(request.args.get('page', 1))
    per_page = 10
    sort_by = request.args.get('sort', 'last_name')
    session_id = request.args.get('session_id')
    academic_year_id = request.args.get('academic_year_id')
    
    offset = (page - 1) * per_page

    academic_year = AcademicYear.query.filter_by(id=academic_year_id).first() if academic_year_id else None
    sessions = Session.query.filter_by(academic_year_id=academic_year_id).all() if academic_year_id else Session.query.all()
    academic_years = AcademicYear.query.all()

    class_dict = {
    cls.id: {
        'name': cls.name,
        'tuition': cls.tuition,
        'currency': cls.currency
    }
    for cls in Class.query.filter_by(company_id=company_id).all()
}


    students_query = (
        db.session.query(Student)
        .join(Session)
        .join(User)
        .filter(Student.company_id == company_id)
    )
    
    if session_id:
        students_query = students_query.filter(Student.session_id == session_id)
    if academic_year:
        students_query = students_query.filter(Session.academic_year_id == academic_year.id)
    
    if sort_by == 'last_name':
        students_query = students_query.order_by(User.last_name)
    elif sort_by == 'first_name':
        students_query = students_query.order_by(User.first_name)
    elif sort_by == 'remaining_fees':
        students_query = students_query.order_by(
            func.sum(Installment.amount) - Class.tuition
        )
    
    total_students = students_query.count()
    students = students_query.offset(offset).limit(per_page).all()
    total_pages = ceil(total_students / per_page)

    return render_template(
        'dashboard/@support_team/school/manage_student_fees.html',
        students=students,
        sessions=sessions,
        academic_years=academic_years,
        class_dict=class_dict,
        page=page,
        total_pages=total_pages,
        company=company,
        academic_year=academic_year
    )

@accounting.route("/manage_wages/<int:company_id>")
@login_required
@school_accountant_required
def manage_wages(company_id):
    company = Company.query.get_or_404(company_id)

    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    excluded_roles = ['Student', 'School Admin', 'Parent']
    excluded_role_ids = [role.id for role in Role.query.filter(Role.name.in_(excluded_roles)).all()]

    employees_query = User.query.filter(
        User.company_id == company_id,
        User.role_id.notin_(excluded_role_ids)
    )
    
    total_employees = employees_query.count()
    employees = employees_query.offset(offset).limit(per_page).all()

    wages = Wage.query.join(User).filter(User.company_id == company_id).all()

    employee_wages = [
        {
            'user': emp,
            'name': f"{emp.first_name} {emp.last_name}" if emp.first_name and emp.last_name else emp.email,
            'profile_picture': emp.profile_picture_url,
            'role': emp.role.name,
            'wage': next((w for w in wages if w.user_id == emp.id), None) if not emp.is_teacher() else {
                'amount': emp.teachers[0].wage if emp.teachers else 'N/A',
                'currency': emp.teachers[0].currency if emp.teachers else 'N/A',
                'system': emp.teachers[0].wage_system if emp.teachers else 'N/A'
            }
        }
        for emp in employees
    ]

    total_pages = ceil(total_employees / per_page)

    return render_template(
        'dashboard/@support_team/school/manage_wages.html',
        employees=employee_wages,
        company=company,
        page=page,
        total_pages=total_pages
    )


@accounting.route("/manage_expenses/<int:company_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@school_accountant_required
def manage_expenses(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        amount = request.form.get('amount')
        currency = request.form.get('currency')
        category = request.form.get('category')
        description = request.form.get('description')
        date = request.form.get('date')

        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
        else:
            date = datetime.utcnow()

        new_expense = Expense(
            amount=amount,
            currency=currency,
            category=category,
            description=description,
            date=date,
            company_id=company.id
        )

        db.session.add(new_expense)
        db.session.commit()

        role = Role.query.filter_by(name='CEO').first()
        if role:
            ceo_user = User.query.filter_by(role_id=role.id).first()
            ceo_email = ceo_user.email
            notify_ceo(
                ceo_email,
                currency,
                amount,
                category
            )

                
        """
        
        main_admin = User.query.filter_by(role='Main Admin').first()
        if main_admin:
            msg = Message("New Expense Created",
                          sender="noreply@yourdomain.com",
                          recipients=[main_admin.email])
            msg.body = f"New expense created:\n\n" \
                       f"Title: {category}\n" \
                       f"Amount: {amount} {currency}\n" \
                       f"Date: {date.strftime('%Y-%m-%d')}\n" \
                       f"Description: {description}"
            mail.send(msg)

        """
        flash('Facture ajoutée!', 'success')
        return redirect(url_for('accounting.manage_expenses', company_id=company.id))

    elif request.method == 'PUT':
        expense_id = int(request.form.get('expense_id'))
        expense = Expense.query.get_or_404(expense_id)

        expense.amount = float(request.form.get('amount'))
        expense.currency = request.form.get('currency')
        expense.category = request.form.get('category')
        expense.description = request.form.get('description', '')
        expense.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d') if request.form.get('date') else expense.date

        db.session.commit()
        flash('Facture mise à jour!', 'success')
        return redirect(url_for('accounting.manage_expenses', company_id=company.id))

    elif request.method == 'DELETE':
        expense_id = int(request.form.get('expense_id'))
        expense = Expense.query.get_or_404(expense_id)

        db.session.delete(expense)
        db.session.commit()
        flash('Facture supprimée!', 'success')
        return redirect(url_for('accounting.manage_expenses', company_id=company.id))

    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    expenses_query = Expense.query.filter_by(company_id=company.id).order_by(Expense.date.desc())
    total_expenses = expenses_query.count()
    expenses = expenses_query.offset(offset).limit(per_page).all()

    total_pages = ceil(total_expenses / per_page)

    return render_template(
        'dashboard/@support_team/school/manage_expenses.html',
        expenses=expenses,
        page=page,
        total_pages=total_pages,
        company=company
    )