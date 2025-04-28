from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous import Serializer
from flask_login import UserMixin
from ... import db, login_manager
import os
from .role import Role
from ..school.grade import Grade
from ..school.friendship import Friendship
from ..school.friendship import friends
from sqlalchemy.orm import aliased
from flask_login import current_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    first_name = db.Column(db.String(64), default=" ")
    last_name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.DateTime(), default=datetime.utcnow)
    place_of_birth = db.Column(db.String(), default='Niamey')
    username = db.Column(db.String(64))
    name = db.Column(db.String(64))
    gender = db.Column(db.String())
    address = db.Column(db.String())
    profile_picture_url = db.Column(db.String)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    wages = db.relationship('Wage', backref='user', lazy=True)
    contacts = db.relationship('Contact', back_populates='user', lazy='dynamic')

    remember_token = db.Column(db.String(100))
    remember_token_expiry = db.Column(db.DateTime)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))


    files = db.relationship('File', backref='user', lazy=True)


    email_username = db.Column(db.String())
    email_password = db.Column(db.String())
    email_provider = db.Column(db.String(), default='gmail')
    smtp_server = db.Column(db.String())
    smtp_port = db.Column(db.Integer, default=587)
    imap_server = db.Column(db.String())
    imap_port = db.Column(db.Integer, default=993)
    
    # Transport&logistics specific relationships
    products = db.relationship('Product', backref='author', lazy=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    authorizations = db.relationship('Authorization', backref='user', lazy='dynamic')
    purchases = db.relationship('Purchase', back_populates='user', lazy=True)
    tasks = db.relationship('Task', lazy=True)
    docs = db.relationship('Doc', backref='user', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')

    # Specific relationships for school system
    grades = db.relationship('Grade', backref='student', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    book_loans = db.relationship('BookLoan', backref='user', lazy=True)
    students = db.relationship('Student', back_populates='user', lazy=True)

    # General employee information
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.String)
    department = db.Column(db.String)
    phone_number = db.Column(db.String)

    
    # These columns can be used for storing
    # informations for service mutations 
    arrival_date = db.Column(db.DateTime())
    leaving_date = db.Column(db.DateTime())
    transport_company = db.Column(db.String)
    transport_type = db.Column(db.String)
    transport_costs = db.Column(db.String)
    current_location = db.Column(db.String)



    # Transport & Logistics
    transport_license = db.Column(db.String)

    # Public Works
    project_role = db.Column(db.String)
    certification = db.Column(db.String)


    social_security_number = db.Column(db.String(64))
    bank_account_number = db.Column(db.String(64))
    bank_name = db.Column(db.String(128))
    routing_number = db.Column(db.String(64))
    emergency_contact_name = db.Column(db.String(128))
    emergency_contact_phone = db.Column(db.String(64))
    certifications = db.Column(db.Text)  # List of certifications
    training_records = db.Column(db.Text)  # Details of training received
    contract_start_date = db.Column(db.DateTime, default=datetime.utcnow)  # Contract start date
    contract_end_date = db.Column(db.DateTime, default=datetime.utcnow)  # Contract end date
    employment_terms = db.Column(db.Text)
    service_name = db.Column(db.String())
    registration_number = db.Column(db.String(), default='1254')

    # Electricity
    electrical_certification = db.Column(db.String)
    safety_training = db.Column(db.String)

    # Plumbing
    plumbing_certification = db.Column(db.String)
    tool_expertise = db.Column(db.String)

    # Electronics
    electronics_certification = db.Column(db.String)
    tech_skills = db.Column(db.String)

    # Biology
    lab_certifications = db.Column(db.String)
    research_interests = db.Column(db.String)

    # Oil, gas and Water exploitation
    pipeline_id = db.Column(db.Integer(), db.ForeignKey('pipelines.id'))

    blood_group = db.Column(db.String())

    signature_name = db.Column(db.String(128))
    signature_title = db.Column(db.String(128))
    signature_phone = db.Column(db.String(64))
    signature_word = db.Column(db.String) # eg : Kind Regards,...
    signature_additional_badge = db.Column(db.String)
    signature_html = db.Column(db.Text)

    folders = db.relationship('Folder', backref='owner', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def get_remember_token(self, expires_in=30*86400):  # 30 days
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_remember_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['user_id'])

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    


    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        return True
    
   

    def assign_role(self):
        roles = {
            current_app.config['RESSYNC_CEO']:'SAILSMARK_Ceo',
            current_app.config['RESSYNC_HR_MANAGER']:'Ressync_HR_Manager',
            current_app.config['RESSYNC_ACCOUNTANT']:'Ressync_Accountant',
        }
        agents_emails = os.getenv("RESSYNC_AGENTS_EMAILS")
        RESSYNC_AGENTS_EMAILS = agents_emails.split(',')

        if self.email in roles:
            role_name = roles[self.email]
            self.role = Role.query.filter_by(name=role_name).first()
        elif self.email in RESSYNC_AGENTS_EMAILS:
            self.role = Role.query.filter_by(name='Employee').first()
        else:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def role_names(self):
        return [self.role.name] if self.role else []

    def has_role(self, role_name):
        return self.role and self.role.name == role_name

    def is_role(self, role_name):
        return self.has_role(role_name)
    
    def has_position(self, position_title):
        return self.role and self.role.position == position_title


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.assign_role()

    def is_employee(self):
        return self.role.name == 'Employee'
    
    def is_administrator(self):
        return self.role.name == 'Administrator'

    def is_hr_manager(self):
        return self.role.name == 'HR Manager'

    def is_accountant(self):
        return self.role.name == 'Accountant'

    def is_project_manager(self):
        return self.role.name == 'Project Manager'

    def is_ceo(self):
        return self.role.name == 'CEO'

    def is_user(self):
        return self.role.name == 'User'

    def is_reseller(self):
        return self.role.name == 'Reseller'
    
    # Position-based methods for company positions
    def is_responsible(self):
        return self.has_position('responsible')
    
    def is_company_it_administrator(self):
        return self.has_position('IT Administrator')

    def is_agent(self):
        return self.has_position('agent')

    def is_consultant(self):
        return self.has_position('consultant')
    
    def is_customer(self):
        return self.has_position('customer')
    
    def is_sales(self):
        return self.has_position('Sales Manager')

    def is_ressync_sales_director(self):
        """Check if the current user is the Ressync Sales Director."""
        ressync_sales_director_email = current_app.config['RESSYNC_SALES_DIRECTOR']
        return current_user.email == ressync_sales_director_email
    



    # School-specific roles
    def is_school_admin(self):
        return self.role.name == 'School Admin'

    def is_school_accountant(self):
        return self.role.name == 'School Accountant'

    def is_school_hr_manager(self):
        return self.role.name == 'School HR Manager'

    def is_librarian(self):
        return self.role.name == 'Librarian'

    def is_teacher(self):
        return self.role.name == 'Teacher'

    def is_parent(self):
        return self.role.name == 'Parent'

    def is_student(self):
        return self.role.name == 'Student'
    
    def is_it_administrator(self):
        return self.role.name == 'School IT Administrator'

    
    # Methods to manage friendships
    def add_friend(self, user):
        if not self.is_friends_with(user):
            self.friends.append(user)
            return self

    def remove_friend(self, user):
        if self.is_friends_with(user):
            self.friends.remove(user)
            return self

    def is_friends_with(self, user):
        return self.friends.filter(friends.c.friend_id == user.id).count() > 0

    def friends_in_common(self, other_user):
        return self.friends.filter(friends.c.friend_id.in_(
            other_user.friends.with_entities(User.id)
        )).count()
    
    
    def friends_in_common(self, other_user):
        subquery = (
            db.session.query(Friendship.friend_id)
            .filter(Friendship.user_id == self.id)
            .subquery()
        )
        return (
            db.session.query(User)
            .join(Friendship, Friendship.friend_id == User.id)
            .filter(Friendship.user_id == other_user.id)
            .filter(Friendship.friend_id.in_(subquery))
            .count()
        )
    
    def is_ressync_sales(email):
        sales_director = os.getenv('RESSYNC_SALES_DIRECTOR')

        if email == sales_director:
            return True
        return False




    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

