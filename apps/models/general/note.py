from ... import db
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    nature = db.Column(db.String)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)  # Foreign Key to Company

    def __init__(self, title, content, nature=None, company_id=None):
        self.title = title
        self.content = content
        self.nature = nature
        self.company_id = company_id
