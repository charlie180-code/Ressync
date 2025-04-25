from ... import db
from datetime import datetime
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(64))
    image_url = db.Column(db.String(255))
    ebook_url = db.Column(db.String(255))
    published_date = db.Column(db.Date, default=datetime.utcnow)
    category = db.Column(db.String(64), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    loans = db.relationship('BookLoan', backref='book', lazy=True)