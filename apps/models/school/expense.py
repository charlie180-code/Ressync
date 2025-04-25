from datetime import datetime
from ... import db

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(64), nullable=False)  # e.g., "Office Supplies", "Maintenance"
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    company = db.relationship('Company', back_populates='expenses')

    def __init__(self, amount, category, company_id, currency, description=None, date=None):
        self.amount = amount
        self.category = category
        self.company_id = company_id
        self.currency = currency
        self.description = description
        self.date = date if date else datetime.utcnow()

    def __repr__(self):
        return f"<Expense {self.category}: {self.amount} on {self.date}>"
