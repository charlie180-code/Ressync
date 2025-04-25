from datetime import datetime
from ... import db

class Authorization(db.Model):
    __tablename__ = 'authorizations'
    id = db.Column(db.Integer, primary_key=True)
    client_first_name = db.Column(db.String, nullable=False)
    client_last_name = db.Column(db.String, nullable=False)
    client_phone_number = db.Column(db.String, nullable=False)
    client_email_address = db.Column(db.String)
    client_id_card_url = db.Column(db.String)
    client_signature_url = db.Column(db.String)
    client_location = db.Column(db.String, nullable=False)
    agent_first_name = db.Column(db.String, nullable=False)
    agent_last_name = db.Column(db.String, nullable=False)
    agent_email_address = db.Column(db.String)
    shipping_company_title = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    provider_email1 = db.Column(db.String)
    provider_email2 = db.Column(db.String)
    provider_email3 = db.Column(db.String)
    provider_email4 = db.Column(db.String)
    provider_name1 = db.Column(db.String)
    provider_name2 = db.Column(db.String)
    provider_name3 = db.Column(db.String)
    provider_name4 = db.Column(db.String)
    lading_bills_identifier = db.Column(db.String, nullable=False)
    service_fees = db.Column(db.Float, default=0.0)
    granted = db.Column(db.Boolean, default=False)
    
    company_proof_nif = db.Column(db.String)
    company_proof_rccm = db.Column(db.String)
    company_name = db.Column(db.String)
    is_company = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)