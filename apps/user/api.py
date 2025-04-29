from flask import jsonify
from flask_login import login_required
from .support_team.business.insights import get_employee_stats, get_expense_stats, get_project_stats
from . import user

@user.route('/api/dashboard/company/other/stats/<int:company_id>')
@login_required
def get_dashboard_stats(company_id):
    employee_stats = get_employee_stats(company_id)
    expense_stats = get_expense_stats(company_id)
    project_stats = get_project_stats(company_id)
    
    return jsonify({
        'success': True,
        'data': {
            'employees': employee_stats,
            'expenses': expense_stats,
            'projects': project_stats
        }
    })