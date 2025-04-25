from ... import db
from datetime import datetime


class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    type = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    """
    max grade value indicate how the computations
    are going to be performed based on the grading system
    of the class

    """
    max_grade_value = db.Column(db.String, default='20')
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    teacher = db.relationship('Teacher', backref='exams')
    grades = db.relationship('Grade', backref='exam', lazy=True)
    
    def __init__(self, name, type, max_grade_value, date, subject_id, class_id, session_id, company_id, teacher_id):
        self.name = name
        self.type = type
        self.max_grade_value = max_grade_value
        self.date = date
        self.subject_id = subject_id
        self.class_id = class_id
        self.session_id = session_id
        self.company_id = company_id
        self.teacher_id = teacher_id
