from .. import db
from flask_babel import gettext as _
from .school.classroom import Class
from .school.installment import Installment

roles_translations = {
    'CEO': _('Directeur général'),
    'HR Manager': _('Responsable RH'),
    'Accountant': _('Comptable'),
    'Project Manager': _('Chef de projet'),
    'Sales Manager': _('Responsable des ventes'),
    'IT Administrator': _('Administrateur IT'),
    'Team Leader': _('Chef d\'équipe'),
    'Employee': _('Employé'),
    'User': _('Utilisateur'),
    'Reseller': _('Revendeur'),
    'School Admin': _('Proviseur'),
    'School Accountant': _('Comptable'),
    'School IT Administrator': _('Administrateur IT scolaire'),
    'School HR Manager': _('Responsable RH'),
    'Librarian': _('Bibliothécaire'),
    'Teacher': _('Enseignant'),
    'Parent': _('Parent'),
    'Student': _('Étudiant')
}

def add_installments(class_id, amounts, due_dates):
    class_obj = Class.query.get_or_404(class_id)
    if len(amounts) > 4 or len(due_dates) > 4:
        raise ValueError("Maximum of 4 installments allowed")

    for amount, due_date in zip(amounts, due_dates):
        installment = Installment(amount=amount, due_date=due_date, class_id=class_id)
        db.session.add(installment)
    
    db.session.commit()

