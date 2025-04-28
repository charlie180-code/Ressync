from datetime import datetime
from ... import db

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email_address = db.Column(db.String, nullable=False)
    services = db.Column(db.String)
    job_title = db.Column(db.String, nullable=False)
    wage = db.Column(db.Float, default=0.0)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_birth = db.Column(db.DateTime)
    picture_url = db.Column(db.String)
    identifier = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    def __init__(self, first_name, last_name, email_address, job_title, identifier, company_id, services=None, wage=0.0, member_since=None, date_of_birth=None, picture_url=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.services = services
        self.job_title = job_title
        self.wage = wage
        self.member_since = member_since or datetime.utcnow()
        self.date_of_birth = date_of_birth
        self.picture_url = picture_url
        self.identifier = identifier
        self.company_id = company_id
