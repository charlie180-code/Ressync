from ... import db


class_teacher = db.Table('class_teacher',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
)
