from ... import db

class Installment(db.Model):
    __tablename__ = 'installments'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String)
    due_date = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    def __init__(self, amount, due_date, class_id, student_id, currency, is_paid=True):
        self.amount = amount
        self.due_date = due_date
        self.class_id = class_id
        self.is_paid = is_paid
        self.student_id = student_id
        self.currency = currency
