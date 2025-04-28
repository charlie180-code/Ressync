from flask import make_response, render_template, current_app
from io import BytesIO
import qrcode
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
from flask_babel import gettext as _
from weasyprint import HTML
import base64
from ..models.general.company import Company
from ..models.general.invoice import Invoice
from ..models.general.company_expense import CompanyExpense
from ..auth.utils import generate_invoice_id

def generate_company_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    company = Company.query.get_or_404(invoice.company_id)
    expenses = CompanyExpense.query.filter_by(invoice_id=invoice_id).all()

    qr_code_io = create_qr_code(f"Invoice ID: {invoice.id}\nCompany: {company.title}")
    barcode_io = create_barcode(f"{invoice.id}")

    invoice_data = prepare_company_invoice_data(company, invoice, expenses)

    html_content = render_template(
        'reports/invoices/company_invoice.html',
        invoice_data=invoice_data,
        qr_code_base64=base64.b64encode(qr_code_io.getvalue()).decode('utf-8'),
        barcode_base64=base64.b64encode(barcode_io.getvalue()).decode('utf-8')
    )

    pdf = HTML(string=html_content).write_pdf()
    translated_filename = f"Invoice - {invoice.id}.pdf"
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

def create_barcode(data):
    code128 = barcode.get_barcode_class('code128')
    barcode_img = code128(data, writer=ImageWriter())

    barcode_io = BytesIO()
    barcode_img.write(barcode_io)
    barcode_io.seek(0)

    return barcode_io

def prepare_company_invoice_data(company, invoice, expenses):
    total_amount = sum(expense.unit_price * expense.quantity for expense in expenses)

    return {
        'company_name': company.title,
        'company_logo': company.logo_url,
        'company_address': company.location,
        'company_email': company.email,
        'invoice_id': generate_invoice_id(),
        'invoice_date': invoice.date_created.strftime('%B %d, %Y'),
        'due_date': invoice.due_date.strftime('%B %d, %Y'),
        'expenses': expenses,
        'total_amount': total_amount,
        'client_name': invoice.client_name,
        'client_type': invoice.client_type,
        'client_phone': invoice.client_phone,
        'client_email': invoice.client_email,
        'client_address': invoice.client_address,
        'client_city': invoice.client_city,
        'client_postal_code': invoice.client_postal_code,
        'client_country': invoice.client_country,
        'payment_details': 'All payments should be made to the account details provided.',
        'notes': 'Please retain this invoice for your records.',
        'legal_info': 'All payments should be made to the account details provided. Please retain this invoice for your records.'
    }