from flask import  make_response, render_template, current_app
from io import BytesIO
import qrcode
from datetime import datetime
from flask_babel import gettext as _
from weasyprint import HTML
from ..models.school.student import Student
from ..models.general.company import Company
from ..models.school.session import Session
from ..models.school.academic_year import AcademicYear
from ..models.school.installment import Installment
from ..models.school.classroom import Class
import base64
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
import os
import requests
from sqlalchemy.orm import joinedload
from ..models.general.file import File
import sys
from pathlib import Path



def generate_invoice(student_id):
    student = Student.query.get_or_404(student_id)
    company = Company.query.get_or_404(student.company_id)
    installment = Installment.query.filter_by(student_id=student_id).order_by(Installment.due_date.desc()).first()
    
    if not installment:
        raise Exception("No installment found for this student.")

    qr_code_io = create_qr_code(f"Invoice ID: {installment.id}\nAmount: {installment.amount}\nCurrency: {installment.currency}")

    invoice_data = prepare_invoice_data(student, company, installment)

    html_content = render_template('reports/invoices/installment_receipt.html', invoice_data=invoice_data, qr_code_base64=base64.b64encode(qr_code_io.getvalue()).decode('utf-8'))

    pdf = HTML(string=html_content).write_pdf()    

    translated_filename = f"{_('Reçu_inscription')} - {installment.id}.pdf"
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={translated_filename}'

    return response


def create_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')

    qr_code_io = BytesIO()
    qr_img.save(qr_code_io, format='PNG')
    qr_code_io.seek(0)

    return qr_code_io

def prepare_invoice_data(student, company, installment):

    student_class = Class.query.get(student.class_id)
    
    session = Session.query.get(student_class.session_id)
    
    academic_year = AcademicYear.query.get(session.academic_year_id)

    if student_class.tuition > 0:
        tuition_fees = student_class.tuition
    elif academic_year and academic_year.tuition_fees > 0:
        tuition_fees = academic_year.tuition_fees
    else:
        tuition_fees = 0

    remaining_fees = tuition_fees - installment.amount if tuition_fees > 0 else 0

    return {
        'company_name': company.title,
        'company_logo': company.logo_url,
        'company_address': company.location,
        'company_email':company.email,
        'student_full_name': f"{student.user.first_name} {student.user.last_name}",
        'student_dob': student.user.date_of_birth.strftime('%Y-%m-%d'),
        'student_gender': student.user.gender,
        'invoice_id': generate_invoice_id(),
        'invoice_date': datetime.utcnow().strftime('%B %d, %Y'),
        'class_name': Class.query.get(student.class_id).name,
        'amount': installment.amount,
        'currency': installment.currency,
        'due_date': installment.due_date.strftime('%B %d, %Y'),
        'tuition_fees': tuition_fees,
        'remaining_amount': remaining_fees if remaining_fees > 0 else 0 
    }

def generate_invoice_id():
    import random
    import datetime

    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_number = random.randint(1000, 9999)
    invoice_id = f"{date_str}-{random_number}"

    return invoice_id


def generate_reset_token(user, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'reset': user.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_reset_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return data['reset']


def save_file_locally(file, folder_name="uploads"):
    """Returns dict with both storage and URL info"""
    base_dir = get_resource_path(folder_name)
    os.makedirs(base_dir, exist_ok=True)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(base_dir, filename)
    
    counter = 1
    name, ext = os.path.splitext(filename)
    while os.path.exists(file_path):
        filename = f"{name}_{counter}{ext}"
        file_path = os.path.join(base_dir, filename)
        counter += 1
    
    file.save(file_path)
    
    return {
        "absolute_path": file_path,
        "filename": filename,
        "url_path": f"/local_files/{folder_name}/{filename}"
    }


def get_resource_path(*relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in a bundle (PyInstaller)
        base_path = Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        base_path = Path.home() / "Documents" / "Ressync"
    
    return str(base_path.joinpath(*relative_path).absolute())

def check_internet_connection():
    url = "https://www.google.com"
    timeout = 8
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.ConnectionError:
        return False
    

def get_company_files(company_id, user_id):
    """
    Retrieve all files associated with a specific company and user.
    """
    # Query all files that are associated with the given company_id and user_id
    files = File.query.filter_by(company_id=company_id, user_id=user_id).all()
    
    return files
