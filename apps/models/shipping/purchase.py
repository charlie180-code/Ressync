from datetime import datetime
from ... import db
class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    author_first_name = db.Column(db.String, nullable=False)
    author_last_name = db.Column(db.String, nullable=False)
    author_email_address = db.Column(db.String, nullable=False)
    author_address = db.Column(db.String, nullable=False)
    product_length = db.Column(db.Float, default=0.0)
    product_width = db.Column(db.Float, default=0.0)
    author_phone_number = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    provider = db.Column(db.String)
    product_picture_url = db.Column(db.String)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False)
    name = db.Column(db.String())
    category = db.Column(db.String)
    doc_url = db.Column(db.String)
    qr_code_url = db.Column(db.String)
    barcode_url = db.Column(db.String)
    service_fees = db.Column(db.Float, default=0.0)
    closed = db.Column(db.Boolean, default=False)
    start_check = db.Column(db.DateTime(), default=datetime.utcnow)

    # Foreign Key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Foreign Key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='purchases')

    def __init__(self, title, token, author_first_name, author_last_name, author_email_address, author_address, author_phone_number, location, description, company_id, product_length=0.0, product_width=0.0, provider=None, product_picture_url=None, name=None, category=None, doc_url=None, qr_code_url=None, barcode_url=None, service_fees=0.0, user_id=None, closed=False, start_check=None):
        self.title = title
        self.token = token
        self.author_first_name = author_first_name
        self.author_last_name = author_last_name
        self.author_email_address = author_email_address
        self.author_address = author_address
        self.product_length = product_length
        self.product_width = product_width
        self.author_phone_number = author_phone_number
        self.location = location
        self.provider = provider
        self.product_picture_url = product_picture_url
        self.description = description
        self.company_id = company_id
        self.name = name
        self.category = category
        self.doc_url = doc_url
        self.qr_code_url = qr_code_url
        self.barcode_url = barcode_url
        self.service_fees = service_fees
        self.user_id = user_id
        self.closed = closed
        self.start_check = start_check or datetime.utcnow()
