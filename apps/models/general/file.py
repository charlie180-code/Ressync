from datetime import datetime
from ... import db

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    filepath = db.Column(db.String)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    def __init__(self, label, filepath, folder_id, user_id, company_id, uploaded_at=None):
        self.label = label
        self.filepath = filepath
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.folder_id = folder_id
        self.user_id = user_id
        self.company_id = company_id
