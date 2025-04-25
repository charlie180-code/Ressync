from ... import db
from datetime import datetime

class Assigment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    grades = db.relationship('Grade', backref='assignment', lazy=True)
    
    def __init__(self, name, type, date, subject_id, class_id, session_id):
        self.name = name
        self.type = type
        self.date = date
        self.subject_id = subject_id
        self.class_id = class_id
        self.session_id = session_id
