from ... import db
from datetime import datetime

class BookLoan(db.Model):
    __tablename__ = 'book_loans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    published_date = db.Column(db.DateTime, default=datetime.utcnow)
    returned = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, book_id, loan_date, return_date, returned, company_id):
        self.user_id = user_id
        self.book_id = book_id
        self.loan_date = loan_date
        self.return_date = return_date
        self.returned = returned
        self.company_id = company_id