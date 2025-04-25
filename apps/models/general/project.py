from datetime import datetime
from ... import db

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_from = db.Column(db.DateTime(), default=datetime.utcnow)
    end_at = db.Column(db.DateTime(), default=datetime.utcnow)
    min_budget = db.Column(db.Float, default=0.0)
    max_budget = db.Column(db.Float, default=0.0)
    debt = db.Column(db.Float, default=0.0)
    status = db.Column(db.Boolean, default=False)  # Changed to Boolean

    # Foreign Key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    def __init__(self, title, objectives, description, start_from=None, end_at=None, min_budget=0.0, max_budget=0.0, debt=0.0, status=False, company_id=None):
        self.title = title
        self.objectives = objectives
        self.description = description
        self.start_from = start_from or datetime.utcnow()
        self.end_at = end_at or datetime.utcnow()
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.debt = debt
        self.status = status
        self.company_id = company_id
