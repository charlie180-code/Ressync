from datetime import datetime
from ... import db

class Doc(db.Model):
    __tablename__ = 'docs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    doc_url = db.Column(db.String, nullable=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    def __init__(self, title, doc_url, user_id, company_id, last_modified=None):
        self.title = title
        self.doc_url = doc_url
        self.last_modified = last_modified or datetime.utcnow()
        self.user_id = user_id
        self.company_id = company_id
