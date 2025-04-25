from ... import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    status = db.Column(db.String)
    start_from = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    report = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    def __init__(self, title, company_id, status=None, start_from=None, end_at=None, report=None):
        self.title = title
        self.status = status
        self.start_from = start_from
        self.end_at = end_at
        self.report = report
        self.company_id = company_id
