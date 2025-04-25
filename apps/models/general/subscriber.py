from ... import db
class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    source = db.Column(db.String)

    # Foreign Key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    def __init__(self, email, company_id, phone=None, source=None):
        self.email = email
        self.company_id = company_id
        self.phone = phone
        self.source = source
