from ... import db
from datetime import datetime

class AudioBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    narrator = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in seconds
    release_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    audio_url = db.Column(db.String(255), nullable=True)  # URL to the audio file
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AudioBook {self.title} by {self.author}>'