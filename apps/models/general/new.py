from datetime import datetime
from ... import db

class New(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    short_text = db.Column(db.String())
    content = db.Column(db.Text)

