from datetime import datetime
from ... import db

class Talk(db.Model):
    __tablename__ = 'talks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    client_email = db.Column(db.String)
    client_phone = db.Column(db.String)

