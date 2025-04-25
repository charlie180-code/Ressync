from datetime import datetime
from ... import db

class MarketingCampaign(db.Model):
    __tablename__ = 'marketing_campaigns'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    start_from = db.Column(db.DateTime(), default=datetime.utcnow)
    end_at = db.Column(db.DateTime(), default=datetime.utcnow)
    min_budget = db.Column(db.Float, default=0.0)
    max_budget = db.Column(db.Float, default=0.0)
    debt = db.Column(db.Float, default=0.0)
    
    # Foreign Key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    def __init__(self, title, description, objectives, start_from=None, end_at=None, min_budget=0.0, max_budget=0.0, debt=0.0, company_id=None):
        self.title = title
        self.description = description
        self.objectives = objectives
        self.start_from = start_from or datetime.utcnow()
        self.end_at = end_at or datetime.utcnow()
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.debt = debt
        self.company_id = company_id
