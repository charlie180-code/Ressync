from ... import db
from datetime import datetime

class Library(db.Model):
    __tablename__ = 'libraries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))

    def __init__(self, name, company_id, section_id, created_at):
        self.name = name
        self.created_at = created_at
        self.company_id = company_id
        self.section_id = section_id