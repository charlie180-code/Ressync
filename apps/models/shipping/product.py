from datetime import datetime
from ... import db


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer)
    category = db.Column(db.String, nullable=False)
    provider = db.Column(db.String)
    provider_location = db.Column(db.String)
    product_img_url = db.Column(db.String)
    publish = db.Column(db.Boolean, nullable=False)
    barcode_url = db.Column(db.String)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 

    def __repr__(self):
        return f'<Product {self.title}>'


