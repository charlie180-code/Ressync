from ... import db

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False, default=0.0)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'))
    
    def __init__(self, value, student_id, subject_id, teacher_id, exam_id, session_id):
        self.value = value
        self.student_id = student_id
        self.subject_id = subject_id
        self.teacher_id = teacher_id
        self.exam_id = exam_id
        self.session_id = session_id