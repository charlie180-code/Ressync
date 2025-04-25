from ... import db


student_exams = db.Table('student_exams',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('exam_id', db.Integer, db.ForeignKey('exams.id'), primary_key=True)
)