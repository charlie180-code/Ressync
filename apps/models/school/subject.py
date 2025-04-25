from ... import db
from .subject_teacher import subject_teacher
from .class_subject import class_subject


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    weight = db.Column(db.Integer, default=1)
    classes = db.relationship('Class', secondary=class_subject, back_populates='subjects')
    teachers = db.relationship('Teacher', secondary=subject_teacher, back_populates='subjects')
