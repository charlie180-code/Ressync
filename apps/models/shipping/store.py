from datetime import datetime
from ... import db
class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    logo_file_url = db.Column(db.String)
    phone = db.Column(db.String)

    # Foreign Key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)


    def __init__(self, name, location, email, company_id, logo_file_url=None, phone=None):
        self.name = name
        self.location = location
        self.email = email
        self.company_id = company_id
        self.logo_file_url = logo_file_url
        self.phone = phone
