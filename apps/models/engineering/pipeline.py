from ... import db
from datetime import datetime

class Pipeline(db.Model):
    __tablename__ = 'pipelines'
    id = db.Column(db.Integer, primary_key=True)
    pipeline_name = db.Column(db.String, default='Station 001')
    pipeline_identifier = db.Column(db.String, default='Old Prague')  # Identifier for the pipeline the employee is working on
    pipeline_type = db.Column(db.String)  # Type of pipeline (e.g., oil, gas, water)
    pipeline_status = db.Column(db.String)  # Current status of the pipeline
    last_inspection_date = db.Column(db.DateTime)  # Date of the last inspection of the pipeline
    next_inspection_date = db.Column(db.DateTime)  # Scheduled date for the next inspection
    maintenance_records = db.Column(db.Text)  # Details of maintenance activities on the pipeline
    pipeline_capacity = db.Column(db.String)  # Capacity of the pipeline
    installed_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the pipeline was installed
    pipeline_location = db.Column(db.String) # pipeline location
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    users = db.relationship('User', backref='station', lazy=True)