from datetime import datetime
from ... import db

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    qr_code_url = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, default='Unpaid')    
    client_name = db.Column(db.String)
    client_type = db.Column(db.String)
    client_phone = db.Column(db.String)
    client_email = db.Column(db.String)
    client_address = db.Column(db.String)
    client_city = db.Column(db.String)
    client_postal_code = db.Column(db.String)
    client_country = db.Column(db.String)
    client_details = db.Column(db.JSON)
    expenses = db.relationship('CompanyExpense', backref='invoice', lazy=True)
