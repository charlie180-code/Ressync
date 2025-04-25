from datetime import datetime
from ... import db

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_first_name = db.Column(db.String)
    employee_last_name = db.Column(db.String)
    employee_email_address = db.Column(db.String, nullable=False)
    employee_services = db.Column(db.String)
    employee_job_title = db.Column(db.String, nullable=False)
    employee_wage = db.Column(db.Float, default=0.0)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    employee_date_of_birth = db.Column(db.DateTime)
    picture_url = db.Column(db.String)
    qr_code_url = db.Column(db.String)
    professional_card_url = db.Column(db.String)
    identifier = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    def __init__(self, employee_first_name, employee_last_name, employee_email_address, employee_job_title, identifier, company_id, employee_services=None, employee_wage=0.0, member_since=None, employee_date_of_birth=None, picture_url=None, qr_code_url=None, professional_card_url=None):
        self.employee_first_name = employee_first_name
        self.employee_last_name = employee_last_name
        self.employee_email_address = employee_email_address
        self.employee_services = employee_services
        self.employee_job_title = employee_job_title
        self.employee_wage = employee_wage
        self.member_since = member_since or datetime.utcnow()
        self.employee_date_of_birth = employee_date_of_birth
        self.picture_url = picture_url
        self.qr_code_url = qr_code_url
        self.professional_card_url = professional_card_url
        self.identifier = identifier
        self.company_id = company_id
