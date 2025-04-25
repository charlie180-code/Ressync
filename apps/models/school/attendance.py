from datetime import date
from ... import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    type_of_attendance = db.Column(db.String)
    number = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    session = db.relationship('Session', back_populates='attendances')

    
    def __init__(self, date, type_of_attendance, number, student_id, session_id):
        self.date = date
        self.type_of_attendance = type_of_attendance
        self.number = number
        self.student_id = student_id
        self.session_id = session_id
