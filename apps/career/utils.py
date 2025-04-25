import base64
import qrcode
from flask import render_template, send_file, url_for, current_app
from io import BytesIO
import openpyxl
from weasyprint import HTML, CSS
from datetime import datetime
import os


def generate_qr_code(data):
    """
    Generates a QR code image for the given data.
    Returns a BytesIO object with the image data.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def save_qr_code_to_static(qr_code_buffer):
    """
    Saves the generated QR code to the static folder and returns the URL for the QR code.
    """
    qr_code_filename = "qr_code.png"
    qr_code_path = os.path.join(current_app.static_folder, qr_code_filename)
    with open(qr_code_path, "wb") as qr_file:
        qr_file.write(qr_code_buffer.getvalue())
    return url_for('static', filename=qr_code_filename)

def generate_pdf(company, employee_data, qr_code_url):
    """
    Generates a PDF with the employee list, including a QR code and timestamp.
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = render_template(
        'reports/company/engineering/employee_list_pdf.html',
        company=company,
        employee_data=employee_data,
        qr_code_url=qr_code_url, 
        current_time=current_time
    )

    css = CSS(string="""
        @page {
            size: A4 landscape;
            margin: 20mm;
        }
    """)

    pdf = HTML(string=html).write_pdf(stylesheets=[css])

    return send_file(BytesIO(pdf), as_attachment=True, download_name="employee_list.pdf", mimetype='application/pdf')



def generate_excel(company, employee_data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Liste des Employés"
    
    headers = ["ID", "First Name", "Last Name", "Fonction", "Matricule", "Pipeline Name", "Address", "Phone Number", "Date of Birth"]
    ws.append(headers)

    for emp in employee_data:
        ws.append([emp['id'], emp['first_name'], emp['last_name'], emp['fonction'], emp['matricule'], emp['pipeline_name'], emp['address'], emp['phone_number'], emp['date_of_birth']])

    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    return send_file(excel_file, as_attachment=True, download_name="employee_list.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')



def generate_badge_qr_code(data):
    """
    Generates a QR code image from the given data and returns a BytesIO object.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def generate_badge(employee, company):
    """
    Generates a badge as a PDF from employee and company data.
    Returns a BytesIO object containing the PDF.
    """
    badge_data = {
        'employee_name': f'{employee.first_name} {employee.last_name}',
        'employee_title': employee.role.name,
        'employee_id': employee.employee_id,
        'company_name': company.title,
        'company_logo_url': company.logo_url,
        'company_address': company.location,
        'company_phone': company.phone_number,
        'company_website_url': company.website_url,
        'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    qr_code_buffer = generate_badge_qr_code(company.website_url)
    qr_code_data_uri = f"data:image/png;base64,{base64.b64encode(qr_code_buffer.getvalue()).decode()}"

    badge_data['qr_code_data_uri'] = qr_code_data_uri

    html = render_template('reports/company/engineering/employee_badge.html', **badge_data)

    css = CSS(string="""
        @page {
            size: A4 portrait;
            margin: 10mm;
        }

        .badge {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 20px;
            border: 2px solid #003366;
            width: 200px;
        }

        .badge img {
            width: 100px;
            height: auto;
            margin-bottom: 10px;
        }

        .badge h2 {
            font-size: 18px;
            color: #003366;
            margin: 5px 0;
        }

        .badge p {
            font-size: 14px;
            color: #555;
            margin: 3px 0;
        }

        .badge .company-info {
            font-size: 12px;
            color: #003366;
            margin-top: 10px;
        }

        .timestamp {
            font-size: 10px;
            color: #aaa;
            margin-top: 5px;
        }

        .qr-code {
            margin-top: 20px;
        }

        .qr-code img {
            width: 50px;
            height: 50px;
        }
    """)

    pdf = HTML(string=html).write_pdf(stylesheets=[css])

    return BytesIO(pdf)