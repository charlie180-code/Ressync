from ... import db
from .class_subject import class_subject
from .class_teacher import class_teacher

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    next_level = db.Column(db.String(64), nullable=False)
    tuition = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String, default="USD")
    """grading system determines how the session averages
    will be calculated
    """
    grading_system = db.Column(db.String(64), nullable=False)
    installments = db.Column(db.Integer, nullable=False, default=4)
    passing_gpa = db.Column(db.Float, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    students = db.relationship('Student', backref='class_', lazy=True)
    teachers = db.relationship('Teacher', secondary=class_teacher, back_populates='classes')
    fee_installments = db.relationship('Installment', backref='classes', lazy=True)
    subjects = db.relationship('Subject', secondary=class_subject, back_populates='classes')
