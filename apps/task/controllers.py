from . import task
from flask_login import login_required, current_user
from flask import render_template, jsonify, request, abort
from ..models.general.task import Task
from ..models.general.user import User
from ..models.general.role import Role
from ..models.general.note import Note
from ..models.general.company import Company
from ..models.utils import roles_translations
from .emails.task_assigner import send_task_assignment_email
from .. import db
from flask_babel import _


@task.route("/tasks/<int:company_id>", methods=["GET", "POST"])
@login_required
def tasks(company_id):
    company = Company.query.get_or_404(company_id)

    if not (current_user.is_responsible() or current_user.is_school_admin()):
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')

        print(assigned_to)

        new_task = Task(
            title=title,
            description=description,
            assigned_to=assigned_to,
            company_id=company.id
        )

        db.session.add(new_task)
        db.session.commit()

        assigner_role = roles_translations.get(current_user.role.name, current_user.role.name)

        send_task_assignment_email(
            company.title, 
            assigned_to, 
            title, 
            description, 
            assigner_role
        )

        return jsonify({'success': True})

    # Define roles based on company category
    role_names = [
        'Employee'
    ]

    # If the company is in the education category, add education-specific roles
    if company.category == 'Education':
        role_names.extend([
            'School Accountant', 'School IT Administrator', 
            'School HR Manager', 'Teacher', 'Librarian'
        ])

    # Fetch users with the relevant roles
    users = User.query.join(Role).filter(
        Role.name.in_(role_names),
        User.company_id == company.id
    ).all()

    # Fetch all tasks associated with the company
    tasks = Task.query.filter_by(company_id=company.id).all()

    # Render the template with tasks and users
    return render_template(
        "dashboard/@support_team/tasks.html", 
        users=users, 
        tasks=tasks, 
        company=company,
        roles_translations=roles_translations
    )

@task.route('/my_tasks/<int:user_id>/company/<int:company_id>')
@login_required
def my_tasks(user_id, company_id):
    company = Company.query.get_or_404(company_id)
    # Ensure the current user is accessing their own tasks
    if current_user.id != user_id:
        abort(403)  # Forbidden

    # Fetch tasks assigned to the current user by user_id
    tasks = Task.query.filter_by(assigned_to=current_user.email).all()

    return render_template('dashboard/@support_team/my_task.html', tasks=tasks, company=company)


@task.route("/manage/task/<int:task_id>/<int:company_id>", methods=["GET", "POST", "DELETE", "PUT"])
@login_required
def manage_task(task_id, company_id):
    company = Company.query.get_or_404(company_id)
    task = Task.query.get_or_404(task_id)

    if request.method == 'GET':
        return jsonify({'success': True, 'task': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'assigned_to': task.assigned_to,
            'company_id': company.id,
        }})

    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.assigned_to = request.form.get('assigned_to')
        task.company_id = company.id
        db.session.commit()

        # Send email notification to the assigned user
        assigned_user = User.query.get(task.assigned_to)
        assigner_role = roles_translations.get(current_user.role.name, current_user.role.name)
        send_task_assignment_email(
            company.title, 
            assigned_user.email, 
            task.title, 
            task.description, 
            assigner_role
        )

        return jsonify({'success': True})

    if request.method == 'PUT':
        data = request.get_json(force=True)
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.assigned_to = data.get('assigned_to', task.assigned_to)
        task.company_id = company.id
        db.session.commit()

        # Send email notification to the assigned user
        assigned_user = User.query.get(task.assigned_to)
        assigner_role = roles_translations.get(current_user.role.name, current_user.role.name)
        send_task_assignment_email(
            company.title, 
            assigned_user.email, 
            task.title, 
            task.description, 
            assigner_role
        )

        return jsonify({'success': True})

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()

        return jsonify({'success': True})
    

@task.route('/tasks/complete/<int:task_id>/company/<int:company_id>', methods=['PUT'])
@login_required
def complete_task(task_id, company_id):
    task = Task.query.get_or_404(task_id)
    company = Company.query.get_or_404(company_id)
    
    if task.status:
        return jsonify({"error": "Cette tâche a été déja effectuée"}), 400
    
    

    task.status = True
    db.session.commit()
    
    return jsonify({"success": "Tâche effectuée"})
