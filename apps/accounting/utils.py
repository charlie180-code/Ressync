from flask import make_response, render_template, current_app, request
from io import BytesIO
import qrcode
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
from flask_babel import gettext as _
from weasyprint import HTML, CSS
import base64
from ..models.general.company import Company
from ..models.general.invoice import Invoice
from ..models.general.company_expense import CompanyExpense
from ..auth.utils import generate_invoice_id
import os

def generate_company_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    company = Company.query.get_or_404(invoice.company_id)
    expenses = CompanyExpense.query.filter_by(invoice_id=invoice_id).all()

    qr_code_io = create_qr_code(f"Invoice ID: {invoice.id}\nCompany: {company.title}")

    invoice_data = prepare_company_invoice_data(company, invoice, expenses)

    html_content = render_template(
        'reports/invoices/company_invoice.html',
        invoice_data=invoice_data,
        qr_code_base64=base64.b64encode(qr_code_io.getvalue()).decode('utf-8'),
    )

    css_path = os.path.join(current_app.root_path, 'static', 'css', 'customs', 'reports', 'invoices', 'company_invoice.css')
    css = CSS(filename=css_path)
    pdf = HTML(string=html_content, base_url=request.root_url).write_pdf(stylesheets=[css])

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


def get_vat_rate(country):
    """Returns VAT rate based on country"""
    vat_rates = {
        'Niger': 0.19,  # 19%
        'France': 0.20,
        'Germany': 0.19,
        'USA': 0.00,    # No VAT
        'Canada': 0.05, # GST
        # Add more countries as needed
    }
    return vat_rates.get(country, 0.00)  # Default to 0% if country not found


def get_currency_format(currency_code):
    """Returns symbol, position (before/after), and spacing for currency"""
    currency_formats = {
        'USD': ('$', 'before', ''),          # $100
        'EUR': ('€', 'before', ''),          # €100
        'XOF': ('CFA', 'after', ' '),        # 100 CFA
        'XAF': ('FCFA', 'after', ' '),       # 100 FCFA
        'NGN': ('₦', 'before', ''),         # ₦100
        'GBP': ('£', 'before', ''),         # £100
        'JPY': ('¥', 'before', ''),         # ¥100
        'CAD': ('CA$', 'before', ''),       # CA$100
        'AUD': ('A$', 'before', ''),       # A$100
        'CNY': ('¥', 'before', ''),        # ¥100
        'INR': ('₹', 'before', ''),        # ₹100
        'RUB': ('₽', 'before', ''),        # ₽100
        'ZAR': ('R', 'before', ' '),       # R 100
        'BRL': ('R$', 'before', ''),       # R$100
        'MXN': ('MX$', 'before', ''),      # MX$100
        'CHF': ('CHF', 'before', ' '),     # CHF 100
        'SEK': ('kr', 'after', ' '),       # 100 kr
        'NOK': ('kr', 'after', ' '),       # 100 kr
        'DKK': ('kr', 'after', ' '),       # 100 kr
        'PLN': ('zł', 'after', ' '),       # 100 zł
        'TRY': ('₺', 'before', ''),        # ₺100
        'AED': ('د.إ', 'before', ' '),     # د.إ 100
        'SAR': ('﷼', 'before', ' '),       # ﷼ 100
        'KRW': ('₩', 'before', ''),        # ₩100
        'SGD': ('S$', 'before', ''),       # S$100
        'HKD': ('HK$', 'before', ''),      # HK$100
        'THB': ('฿', 'before', ''),        # ฿100
        'IDR': ('Rp', 'before', ' '),      # Rp 100
        'MYR': ('RM', 'before', ' '),      # RM 100
        'PHP': ('₱', 'before', ''),        # ₱100
        'VND': ('₫', 'after', ' '),        # 100 ₫
    }
    return currency_formats.get(currency_code, (currency_code, 'before', ' '))

def format_currency_amount(amount, currency_code):
    """Formats the amount with currency symbol in correct position"""
    symbol, position, spacing = get_currency_format(currency_code)
    formatted_amount = "{:,.2f}".format(amount)
    
    if position == 'before':
        return f"{symbol}{spacing}{formatted_amount}"
    else:
        return f"{formatted_amount}{spacing}{symbol}"


def get_currency_symbol(currency_code):
    """Returns the currency symbol for a given currency code"""
    currency_symbols = {
        'USD': '$',          # US Dollar
        'EUR': '€',          # Euro
        'XOF': 'CFA',        # West African CFA franc
        'XAF': 'FCFA',       # Central African CFA franc
        'NGN': '₦',         # Nigerian Naira
        'GBP': '£',         # British Pound
        'JPY': '¥',         # Japanese Yen
        'CAD': 'CA$',      # Canadian Dollar
        'AUD': 'A$',       # Australian Dollar
        'CNY': '¥',        # Chinese Yuan
        'INR': '₹',        # Indian Rupee
        'RUB': '₽',        # Russian Ruble
        'ZAR': 'R',        # South African Rand
        'BRL': 'R$',      # Brazilian Real
        'MXN': 'MX$',      # Mexican Peso
        'CHF': 'CHF',      # Swiss Franc
        'SEK': 'kr',       # Swedish Krona
        'NOK': 'kr',       # Norwegian Krone
        'DKK': 'kr',       # Danish Krone
        'PLN': 'zł',       # Polish Zloty
        'TRY': '₺',        # Turkish Lira
        'AED': 'د.إ',      # UAE Dirham
        'SAR': '﷼',        # Saudi Riyal
        'KRW': '₩',       # South Korean Won
        'SGD': 'S$',       # Singapore Dollar
        'HKD': 'HK$',      # Hong Kong Dollar
        'THB': '฿',       # Thai Baht
        'IDR': 'Rp',       # Indonesian Rupiah
        'MYR': 'RM',       # Malaysian Ringgit
        'PHP': '₱',        # Philippine Peso
        'VND': '₫',        # Vietnamese Dong
    }
    return currency_symbols.get(currency_code, currency_code)  # Default to code if symbol not found

def convert_currency(amount, from_currency, to_currency):
    """Mock currency conversion - in production, use a real API"""
    conversion_rates = {
        'USD': {'EUR': 0.85, 'XOF': 550, 'NGN': 410},
        'EUR': {'USD': 1.18, 'XOF': 655, 'NGN': 480},
        'XOF': {'USD': 0.0018, 'EUR': 0.0015, 'NGN': 0.75},
    }
    
    if from_currency == to_currency:
        return amount
    
    try:
        rate = conversion_rates[from_currency][to_currency]
        return amount * rate
    except KeyError:
        return amount  # Default to original amount if conversion not available

def prepare_company_invoice_data(company, invoice, expenses):
    # Get currencies
    company_currency = company.currency or 'USD'
    client_currency = invoice.preferred_currency or company_currency

     
    # Get currency symbols
    company_currency_symbol = get_currency_symbol(company_currency)
    client_currency_symbol = get_currency_symbol(client_currency)
    company_currency_format = get_currency_format(company_currency)
    client_currency_format = get_currency_format(client_currency)
    
    # Initialize totals in company currency
    total_gains = 0.0
    total_losses = 0.0
    
    # First calculate all amounts in their original currencies
    for expense in expenses:
        amount = expense.unit_price * expense.quantity
        if expense.currency != company_currency:
            # Convert to company currency first
            amount = convert_currency(amount, expense.currency, company_currency)
            
        if expense.is_gain:
            total_gains += amount
        else:
            total_losses += amount
    
    net_amount = total_gains - total_losses
    
    # Get VAT rate based on client country
    vat_rate = get_vat_rate(invoice.client_country)
    vat_amount = net_amount * vat_rate
    total_amount = net_amount + vat_amount
    
    # Convert all amounts to client's preferred currency if different
    if client_currency != company_currency:
        net_amount_converted = convert_currency(net_amount, company_currency, client_currency)
        vat_amount_converted = convert_currency(vat_amount, company_currency, client_currency)
        total_amount_converted = convert_currency(total_amount, company_currency, client_currency)
    else:
        net_amount_converted = net_amount
        vat_amount_converted = vat_amount
        total_amount_converted = total_amount
    
    # Prepare expense details with converted amounts
    processed_expenses = []
    for expense in expenses:
        expense_data = {
            'service_type': expense.service_type,
            'unit_price': expense.unit_price,
            'quantity': expense.quantity,
            'currency': expense.currency,
            'details': expense.details,
            'is_gain': expense.is_gain,
            'original_amount': expense.unit_price * expense.quantity,
            'converted_amount': convert_currency(expense.unit_price * expense.quantity, expense.currency, client_currency) if expense.currency != client_currency else expense.unit_price * expense.quantity
        }
        processed_expenses.append(expense_data)
    
    return {
        'company_name': company.title,
        'company_logo': company.logo_url,
        'company_address': company.location,
        'company_capital_social': company.capital_social,
        'company_nif': company.nif,
        'company_rccm': company.rccm,
        'company_email': company.email,
        'company_phone': company.phone_number,
        'company_website': company.website_url,
        'company_currency': company_currency,
        'company_currency_symbol': company_currency_symbol,
        'company_currency_symbol': company_currency_format[0],
        'company_currency_position': company_currency_format[1],
        'company_currency_spacing': company_currency_format[2],
        'client_currency': client_currency,
        'client_currency_symbol': client_currency_symbol,
        'client_currency': client_currency,
        'client_currency_symbol': client_currency_format[0],
        'client_currency_position': client_currency_format[1],
        'client_currency_spacing': client_currency_format[2],
        'format_currency': format_currency_amount,
        'invoice_id': generate_invoice_id(),
        'invoice_date': invoice.date_created.strftime('%B %d, %Y'),
        'due_date': invoice.due_date.strftime('%B %d, %Y'),
        'expenses': processed_expenses,
        'total_gains': total_gains,
        'total_losses': total_losses,
        'net_amount': net_amount,
        'vat_rate': vat_rate * 100,  # As percentage
        'vat_amount': vat_amount,
        'total_amount': total_amount,
        'net_amount_converted': net_amount_converted,
        'vat_amount_converted': vat_amount_converted,
        'total_amount_converted': total_amount_converted,
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