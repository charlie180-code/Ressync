from ... import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    """
    position column should tell if the user is an agent in the company
    a team leader, an external consultant, a customer etc..
    
    """
    position = db.Column(db.String())

    description = db.Column(db.String(255))
    users = db.relationship('User', backref='role', lazy='dynamic')

    @classmethod
    def insert_roles(cls):
        """
            This is function is just to allow the company It Admin to
            better manage the accesses in the company, he can edit and
            extend role names, descriptions and accesses..

            There are general roles that are for company agents, for
            heads and for simple customers...

            #######################################################
            new roles should be only created and edited by the
            company it admins;
            #######################################################

        """
        roles = {
            'SAILSMARK_Ceo': {'description': "Oversee sailsmark operations and strategy", 'position': 'CEO'},
            'Ressync_HR_Manager': {'description': 'Manage human resources tasks and employee relations for Ressync', 'position': 'HR Manager'},
            'Ressync_Accountant': {'description': 'Handle financial tasks, bookkeeping, and transactions for Ressync', 'position': 'Accountant'},
            'Ressync_Sales_Director': {'description': 'Oversee sales operations and strategies for Ressync', 'position': 'Ressync Sales Director'},
            'CEO': {'description': 'Oversee all company operations and strategy', 'position': 'responsible'},
            'HR Manager': {'description': 'Manage human resources tasks and employee relations', 'position': 'responsible'},
            'Accountant': {'description': 'Handle financial tasks, bookkeeping, and transactions', 'position': 'responsible'},
            'Project Manager': {'description': 'Oversee project planning, execution, and completion', 'position': 'responsible'},
            'Sales Manager': {'description': 'Manage sales activities, analyse marketing data', 'position': 'Sales Manager'},
            'IT Administrator': {'description': 'Manage and support IT infrastructure and systems', 'position': 'IT Administrator'},
            'Team Leader': {'description': 'Lead and coordinate tasks within a specific team', 'position': 'responsible'},
            'Employee': {'description': 'Perform tasks and duties assigned in their specific role', 'position': 'agent'},
            'User': {'description': 'A generic user role', 'position': 'customer'},
            'Reseller': {'description': 'Offer and manage products for other users', 'position': 'consultant'},
            # School-specific roles
            'School Admin': {'description': 'Manage school operations including sessions, teachers, students, grades, sections, subjects, and classes', 'position': 'School Admin'},
            'School Accountant': {'description': 'Manage school finances, student fees, and personal wages', 'position': 'School Accountant'},
            'School IT Administrator': {'description': 'Manage and support school IT infrastructure and systems', 'position': 'School IT Administrator'},
            'School HR Manager': {'description': 'Manage school personnel including teachers and students', 'position': 'School HR Manager'},
            'Librarian': {'description': 'Manage book lending and ensure timely returns', 'position': 'Librarian'},
            'Teacher': {'description': 'Submit assignments, take attendance, add quizzes/exams, create grading rules, calculate averages, and print student records', 'position': 'Teacher'},
            'Parent': {'description': 'View children’s grades, due fees, attendance, and reports', 'position': 'Parent'},
            'Student': {'description': 'View own grades, attendance, borrowed books, and due dates', 'position': 'Student'}
        }
        
        for role_name, details in roles.items():
            role = cls.query.filter_by(name=role_name).first()
            if role is None:
                role = cls(name=role_name)
            role.description = details['description']
            role.position = details['position']
            role.default = (role_name == 'User')
            db.session.add(role)
        db.session.commit()
