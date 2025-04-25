from ... import db
from datetime import datetime
from .student_subject import student_subjects
from .student_exam import student_exams

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='students')
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    subjects = db.relationship('Subject', secondary=student_subjects, backref=db.backref('students', lazy='dynamic'))
    exams = db.relationship('Exam', secondary=student_exams, backref=db.backref('students', lazy='dynamic'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    installments = db.relationship('Installment', backref='student', lazy=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))
    
    

