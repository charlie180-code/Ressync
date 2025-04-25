from ... import db

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    tuition_fees = db.Column(db.Float)
    currency = db.Column(db.String(3))
    sessions = db.relationship('Session', backref='academic_year', lazy=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    active = db.Column(db.Boolean, default=True)
