from ... import db

# Association table for classes and subjects
class_subject = db.Table('class_subject',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
)
