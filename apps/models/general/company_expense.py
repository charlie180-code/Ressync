from datetime import datetime
from ... import db
from sqlalchemy.ext.hybrid import hybrid_property

class CompanyExpense(db.Model):
    __tablename__ = 'company_expenses'
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String, nullable=False, default=' ')  # Service type (e.g., Cloud Services, Domain Name, etc.)
    is_gain = db.Column(db.Boolean, default=True)
    details = db.Column(db.JSON)
    currency = db.Column(db.String, default='USD')
    unit_price = db.Column(db.Float)  # Optional: Unit price for the expense
    quantity = db.Column(db.Integer)  # Optional: Quantity for the expense
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    @hybrid_property
    def total_cost(self):
        return (self.unit_price or 0) * (self.quantity or 0)
