from ... import db
from datetime import datetime

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    classes = db.relationship('Class', backref='session', lazy=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    teachers = db.relationship('Teacher', backref='session')
    grades = db.relationship('Grade', backref='grade')
    active = db.Column(db.Boolean, default=False)

    attendances = db.relationship('Attendance', back_populates='session')
    
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'))
    students = db.relationship('Student', backref='session')

    def __init__(self, name, start_date, end_date, company_id, academic_year_id):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.company_id = company_id
        self.academic_year_id = academic_year_id

