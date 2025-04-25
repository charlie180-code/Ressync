from ... import db

# Association table for subjects and teachers
subject_teacher = db.Table('subject_teacher',
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id')),
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'))
)