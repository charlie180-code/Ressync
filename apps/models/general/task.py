from datetime import datetime
from ... import db
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(128))
    
    # Foreign Key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Foreign Key to User
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))


    def __init__(self, title, company_id, assigned_to=None, description=None, status=False):
        self.title = title
        self.company_id = company_id
        self.assigned_to = assigned_to
        self.description = description
        self.status = status