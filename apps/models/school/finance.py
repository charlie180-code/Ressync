from ... import db
from datetime import datetime

class Finance(db.Model):
    __tablename__ = 'finances'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    def __init__(self, description, amount, date, company_id):
        self.description = description
        self.amount = amount
        self.date = date
        self.company_id = company_id