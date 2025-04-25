from flask import request, jsonify
from . import insights
from ..user.support_team.business.insights import (
    count_all_students, calculate_student_count_percentage_difference,
    calculate_student_data_size, count_school_sessions, get_academic_year_for_session
)
from ..models.general.task import Task

@insights.route('/student-count', methods=['GET'])
def get_student_count():
    company_id = request.args.get('company_id')
    student_count = count_all_students(company_id)
    return jsonify({'student_count': student_count})

@insights.route('/student-count-difference', methods=['GET'])
def get_student_count_difference():
    company_id = request.args.get('company_id')
    percentage_difference = calculate_student_count_percentage_difference(company_id)
    return jsonify({'percentage_difference': percentage_difference})

@insights.route('/data-size', methods=['GET'])
def get_data_size():
    company_id = request.args.get('company_id')
    data_size = calculate_student_data_size(company_id)
    return jsonify({'data_size': data_size})

@insights.route('/session-count', methods=['GET'])
def get_session_count():
    company_id = request.args.get('company_id')
    session_count = count_school_sessions(company_id)
    return jsonify({'session_count': session_count})

@insights.route('/academic-year', methods=['GET'])
def get_academic_year():
    company_id = request.args.get('company_id')
    academic_year = get_academic_year_for_session(company_id)
    return jsonify({'academic_year': academic_year})

@insights.route('/get-students-general-avg', methods=['GET'])
def get_students_general_avg():
    company_id = request.args.get('company_id')
    pass


@insights.route('/task-completion', methods=['GET'])
def get_task_completion():
    company_id = request.args.get('company_id')
    
    # Get all tasks for the specified company
    tasks = Task.query.filter_by(company_id=company_id).all()
    
    # Calculate the count of completed and pending tasks
    completed_count = sum(1 for task in tasks if task.status)
    pending_count = len(tasks) - completed_count  # Total tasks minus completed tasks
    
    return jsonify({
        'completed': completed_count,
        'pending': pending_count
    })
