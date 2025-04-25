from ... import db
from .subject_teacher import subject_teacher
from .class_teacher import class_teacher

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    wage = db.Column(db.Float)
    wage_system = db.Column(db.String)
    currency = db.Column(db.String)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subjects = db.relationship('Subject', secondary=subject_teacher, back_populates='teachers')
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    user = db.relationship('User', backref='teachers')
    classes = db.relationship('Class', secondary=class_teacher, back_populates='teachers')