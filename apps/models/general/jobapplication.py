from datetime import datetime
from ... import db
class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = db.Column(db.Integer, primary_key=True)
    applicant_first_name = db.Column(db.String, nullable=False)
    applicant_last_name = db.Column(db.String, nullable=False)
    applicant_email_address = db.Column(db.String, nullable=False)
    applicant_location = db.Column(db.String, nullable=False)
    motivation = db.Column(db.Text, nullable=False)
    linkedin_url = db.Column(db.String)
    github_url = db.Column(db.String)
    dribble_url = db.Column(db.String)
    date_of_birth = db.Column(db.DateTime())
    apply_at = db.Column(db.DateTime(), default=datetime.utcnow)
    CV_url = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='job_applications')
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    status = db.Column(db.String)

    def __init__(self, applicant_first_name, applicant_last_name, applicant_email_address, applicant_location, motivation, job_id, linkedin_url=None, github_url=None, dribble_url=None, date_of_birth=None, CV_url=None, user_id=None, status=None):
        self.applicant_first_name = applicant_first_name
        self.applicant_last_name = applicant_last_name
        self.applicant_email_address = applicant_email_address
        self.applicant_location = applicant_location
        self.motivation = motivation
        self.linkedin_url = linkedin_url
        self.github_url = github_url
        self.dribble_url = dribble_url
        self.date_of_birth = date_of_birth
        self.CV_url = CV_url
        self.user_id = user_id
        self.job_id = job_id
        self.status = status
