from datetime import datetime
from ... import db

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float)
    posted_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    closing_date = db.Column(db.DateTime)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    applications = db.relationship('JobApplication', backref='job', lazy=True)

    def __init__(self, title, description, location, posted_date, company_id, salary=None, closing_date=None):
        self.title = title
        self.description = description
        self.location = location
        self.salary = salary
        self.posted_date = posted_date
        self.closing_date = closing_date
        self.company_id = company_id
