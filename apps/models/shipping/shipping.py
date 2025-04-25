from datetime import datetime
from ... import db

class Shipping(db.Model):
    __tablename__ = 'loadings'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    unity = db.Column(db.String)
    quantity = db.Column(db.Float)
    pricing = db.Column(db.Float())


