from .. import db
import re
from ..models.school.student import Student
from ..models.school.exam import Exam
from ..models.school.grade import Grade
from ..models.school.session import Session
from ..models.school.attendance import Attendance
from ..models.school.report_token import ReportToken
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from flask import url_for
from ..utils import generate_qr_code
import hashlib
import time


def sanitize_filename(filename):
    """
    Sanitize a string to be used as a safe filename.
    Removes any unsafe characters and replaces spaces with underscores.
    """
    filename = filename.strip().replace(" ", "_")
    # Remove any character that is not alphanumeric, an underscore, or a hyphen
    return re.sub(r'(?u)[^-\w.]', '', filename)


def generate_report_token(student_id, session_id):
    """
    Generate a unique token for the student's report.
    
    Args:
    - student_id: ID of the student.
    - session_id: ID of the session.

    Returns:
    - A unique token that can be used to view the report.
    """
    unique_string = f"{student_id}-{session_id}"

    token = hashlib.sha256(unique_string.encode()).hexdigest()

    existing_token = ReportToken.query.filter_by(token=token).first()
    if not existing_token:
        report_token = ReportToken(token=token, student_id=student_id, session_id=session_id)
        db.session.add(report_token)
        db.session.commit()

    return token

def normalize_grade(avg, max_value, grading_system):
    if grading_system == 'French':
        if max_value == 10:
            return (avg / Decimal(10)) * 20
        elif max_value == 20:
            return avg
        elif max_value == 30:
            return (avg / Decimal(30)) * 10
        elif max_value == 40:
            return (avg / Decimal(40)) * 10
        elif max_value == 50:
            return (avg / Decimal(50)) * 10
        else:
            return avg
    elif grading_system == 'FrenchSec':
        if max_value == 10:
            return avg
        elif max_value == 20:
            return (avg / Decimal(20)) * 10
        elif max_value == 30:
            return (avg / Decimal(30)) * 10
        elif max_value == 40:
            return (avg / Decimal(40)) * 10
        elif max_value == 50:
            return (avg / Decimal(50)) * 10
        else:
            return avg 
    elif grading_system == 'Japanese':
        if max_value == 5:
            return (avg / Decimal(5)) * 20
        else:
            return avg
    elif grading_system == 'American_GPA':
        if max_value == 4.0:
            return avg 
        else:
            return avg
    elif grading_system == 'American_AF':
        return avg
    elif grading_system == 'British_Percentage':
        if max_value == 100:
            return avg
        else:
            return avg
    elif grading_system == 'British_Letter':
        return avg
    else:
        return avg



def compute_all_students_gpas(class_, session_id):
    """
    Compute the GPAs for all students in the class.

    Args:
    - class_: The class object.
    - session_id: The session ID.

    Returns:
    - A dictionary with student user IDs as keys and their GPAs as values.
    """
    all_students = class_.students
    all_student_gpas = {}

    for student in all_students:
        gpa_data = compute_student_gpa(student.user_id, session_id)
        all_student_gpas[student.user_id] = gpa_data['gpa']

    return all_student_gpas

def compute_student_gpa(user_id, session_id):
    db.session.expire_all()
    student = Student.query.filter_by(user_id=user_id).first_or_404()
    session = Session.query.get_or_404(session_id)
    class_ = student.class_

    if not class_:
        raise AttributeError("Student is not assigned to any class.")

    total_weight = Decimal(0)
    total_weighted_average = Decimal(0)

    for subject in class_.subjects:
        exams = Exam.query.filter_by(
            subject_id=subject.id,
            session_id=session_id,
            class_id=class_.id
        ).all()

        if not exams:
            continue

        grades = Grade.query.filter_by(
            subject_id=subject.id,
            session_id=session_id,
            student_id=user_id
        ).join(Exam).filter(Exam.id == Grade.exam_id).all()

        if not grades:
            continue

        # Split grades into categories
        devoir_grades = [grade for grade in grades if grade.exam.type == 'devoir']
        interro_grades = [grade for grade in grades if grade.exam.type == 'interro']
        composition_grades = [grade for grade in grades if grade.exam.type == 'composition/examen']

        # Get max grade values only for composition/examen
        max_grade_values = [
            Decimal(exam.max_grade_value) for exam in exams if exam.type == 'composition/examen'
        ]

        # Check the grading system for primary school
        if class_.grading_system in ['FrenchSec', 'French']:
            # Only compositions are considered in primary school
            if composition_grades:
                total_avg = (
                    Decimal(composition_grades[0].value) if len(composition_grades) == 1
                    else (Decimal(sum(g.value for g in composition_grades)) / len(composition_grades))
                )
            else:
                total_avg = Decimal(0)  # No compositions available

        else:
            # For middle/high school, include all grades
            devoir_avg = Decimal(0)
            interro_avg = Decimal(0)
            composition_avg = Decimal(0)

            if devoir_grades:
                devoir_avg = (Decimal(sum(g.value for g in devoir_grades)) / len(devoir_grades))
            if interro_grades:
                interro_avg = (Decimal(sum(g.value for g in interro_grades)) / len(interro_grades))
            if composition_grades:
                composition_avg = (Decimal(sum(g.value for g in composition_grades)) / len(composition_grades))

            # Normalize the averages safely
            normalized_devoir_avg = (
                normalize_grade(devoir_avg, max_grade_values[0], class_.grading_system)
                if devoir_grades else Decimal(0)
            )
            normalized_interro_avg = (
                normalize_grade(interro_avg, max_grade_values[1], class_.grading_system)
                if interro_grades else Decimal(0)
            )
            normalized_composition_avg = (
                normalize_grade(composition_avg, max_grade_values[0], class_.grading_system)  # Use 0 since only composition is needed
                if composition_grades else Decimal(0)
            )

            # Combine normalized averages safely
            total_avg = (normalized_devoir_avg + normalized_interro_avg + normalized_composition_avg) / 3 if (devoir_grades + interro_grades + composition_grades) else Decimal(0)

        # Calculate the weighted average for the subject
        subject_weight = Decimal(subject.weight) if subject.weight is not None else Decimal(1)
        weighted_average = total_avg * subject_weight
        weighted_average = weighted_average.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        total_weighted_average += weighted_average
        total_weight += subject_weight

    # Include 'conduite' and similar checks
    conduite_attendance = Attendance.query.filter_by(
        student_id=user_id,
        session_id=session_id,
        type_of_attendance='conduite'
    ).first()

    conduite_number = Decimal(conduite_attendance.number) if conduite_attendance else Decimal(18)
    conduite_weight = Decimal(1)
    conduite_weighted_average = conduite_number * conduite_weight

    total_weight += conduite_weight
    total_weighted_average += conduite_weighted_average

    overall_gpa = total_weighted_average / total_weight if total_weight else Decimal(0)

    return {'gpa': overall_gpa.quantize(Decimal('0.01'), rounding=ROUND_DOWN)}


def get_rank_label(rank, gender):
    """
    Get the rank label with suffix based on the rank and gender.

    Args:
    - rank: The rank number.
    - gender: The gender of the student ('M' or 'F').

    Returns:
    - A string representing the rank label.
    """
    if rank == 1:
        return f"{rank}{'er' if gender == 'M' else 'ère'}"
    else:
        return f"{rank}ème"

def compute_student_report_fr(user_id, session_id):
    student = Student.query.filter_by(user_id=user_id).first_or_404()
    session = Session.query.get_or_404(session_id)
    class_ = student.class_

    # Generate the token for the report
    report_token = generate_report_token(student.user_id, session_id)

    # Generate the QR code URL
    qr_code_url = generate_qr_code(report_token)

    if not class_:
        raise AttributeError("Student is not assigned to any class.")

    subjects = class_.subjects
    grades_data = []

    total_weight = Decimal(0)
    total_weighted_average = Decimal(0)
    total_class_avg = Decimal(0)
    total_composition_avg = Decimal(0)
    subject_count = 0

    # Compute GPA for all students in the class
    all_student_gpas = compute_all_students_gpas(class_, session_id)

    subject_averages = {}
    for subject in subjects:
        student_class_avg = Decimal(0)
        weighted_average = Decimal(0)
        student_avg = Decimal(0)

        exams = Exam.query.filter_by(
            subject_id=subject.id,
            session_id=session_id,
            class_id=class_.id
        ).all()

        if not exams:
            continue

        max_grade_values = [Decimal(exam.max_grade_value) for exam in exams]

        for other_student in class_.students:
            grades = Grade.query.filter_by(
                subject_id=subject.id,
                session_id=session_id,
                student_id=other_student.user_id
            ).join(Exam).filter(Exam.id == Grade.exam_id).all()

            if not grades:
                continue

            devoir_grades = [grade for grade in grades if grade.exam.type == 'devoir']
            interro_grades = [grade for grade in grades if grade.exam.type == 'interro']
            composition_grades = [grade for grade in grades if grade.exam.type == 'composition/examen']

            num_devoirs = len(devoir_grades)
            num_interros = len(interro_grades)
            num_compositions = len(composition_grades)

            # Compute averages safely
            devoir_avg = (Decimal(sum(g.value for g in devoir_grades)) / num_devoirs) if num_devoirs > 0 else Decimal(0)
            interro_avg = (Decimal(sum(g.value for g in interro_grades)) / num_interros) if num_interros > 0 else Decimal(0)
            composition_avg = (Decimal(sum(g.value for g in composition_grades)) / num_compositions) if num_compositions > 0 else Decimal(0)

            # Determine grading system
            grading_system = class_.grading_system

            if grading_system in ['FrenchSec', 'French']:
                # Only compositions are considered in primary school
                if num_compositions > 0:
                    total_avg = (
                        Decimal(composition_grades[0].value) if num_compositions == 1 else
                        (Decimal(sum(g.value for g in composition_grades)) / num_compositions)
                    )
                else:
                    total_avg = Decimal(0)  # No compositions available
                student_avg = total_avg  # Only compositions for primary school
            else:
                # Normal processing for other grading systems
                normalized_devoir_avg = (
                    normalize_grade(devoir_avg, max_grade_values[0], grading_system) if num_devoirs > 0 else Decimal(0)
                )
                normalized_interro_avg = (
                    normalize_grade(interro_avg, max_grade_values[1], grading_system) if num_interros > 0 else Decimal(0)
                )
                normalized_composition_avg = (
                    normalize_grade(composition_avg, max_grade_values[2], grading_system) if num_compositions > 0 else Decimal(0)
                )

                student_class_avg = (normalized_devoir_avg + normalized_interro_avg) / 2 if (num_devoirs + num_interros) > 0 else Decimal(0)
                student_avg = (student_class_avg + normalized_composition_avg) / 2 if num_compositions > 0 else student_class_avg
                weighted_average = student_avg * Decimal(subject.weight or 1)

            subject_averages[other_student.user_id] = student_avg

            if other_student.user_id == student.user_id:
                weighted_average = student_avg * Decimal(subject.weight or 1)

        if subject_averages:
            sorted_averages = sorted(subject_averages.values(), reverse=True)
            rank = sorted_averages.index(subject_averages[student.user_id]) + 1

            rank_label = get_rank_label(rank, student.user.gender)

            if list(subject_averages.values()).count(subject_averages[student.user_id]) > 1:
                rank_label += " ex"

            appreciation = get_appreciation(student_class_avg)

            grades_data.append({
                'subject': subject.name,
                'coefficient': Decimal(subject.weight or 1),
                'class_avg': student_class_avg.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                'composition_avg': composition_avg.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                'weighted_average': weighted_average.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                'subject_rank': rank_label,
                'appreciation': appreciation,
                'teacher_signature': ''
            })

            total_weight += Decimal(subject.weight or 1)
            total_weighted_average += weighted_average
            total_class_avg += student_class_avg
            total_composition_avg += composition_avg
            subject_count += 1

    # Add 'Conduite' to the report
    conduite_attendance = Attendance.query.filter_by(
        student_id=student.user_id,
        session_id=session_id,
        type_of_attendance='conduite'
    ).first()

    conduite_number = Decimal(conduite_attendance.number) if conduite_attendance else Decimal(18)
    conduite_weight = Decimal(1)
    conduite_weighted_average = conduite_number * conduite_weight

    subject_averages[student.user_id] = conduite_number
    sorted_averages = sorted(subject_averages.values(), reverse=True)
    conduite_rank = sorted_averages.index(subject_averages[student.user_id]) + 1

    conduite_rank_label = get_rank_label(conduite_rank, student.user.gender)

    if list(subject_averages.values()).count(conduite_number) > 1:
        conduite_rank_label += " ex"

    conduite_appreciation = get_appreciation(conduite_number)

    grades_data.append({
        'subject': 'Conduite',
        'coefficient': conduite_weight,
        'class_avg': conduite_number.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        'composition_avg': conduite_number.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        'weighted_average': conduite_weighted_average.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        'subject_rank': conduite_rank_label,
        'appreciation': conduite_appreciation,
        'teacher_signature': ''
    })

    total_weight += conduite_weight
    total_weighted_average += conduite_weighted_average
    total_class_avg += conduite_number
    total_composition_avg += conduite_number
    subject_count += 1

    # Compute overall GPA and rank
    overall_gpa = Decimal(compute_student_gpa(student.user_id, session_id)['gpa'])
    overall_gpa = overall_gpa.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    sorted_gpas = sorted(all_student_gpas.values(), reverse=True)
    rank = sorted_gpas.index(overall_gpa) + 1

    rank_label = get_rank_label(rank, student.user.gender)

    if sorted_gpas.count(overall_gpa) > 1:
        rank_label += " ex"

    lowest_avg = min(all_student_gpas.values()).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    highest_avg = max(all_student_gpas.values()).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    class_avg = (sum(all_student_gpas.values()) / len(all_student_gpas)).quantize(Decimal('0.01'), rounding=ROUND_DOWN) if all_student_gpas else Decimal(0)

    attendance_types = [
        'Absence(s)_justifiée(s)',
        'Absence(s)_non_justifiée(s)',
        'Retard(s)_motivés',
        'Retard(s)_non_motivés'
    ]
    attendance_counts = {atype: 0 for atype in attendance_types}

    attendances = Attendance.query.filter_by(student_id=user_id, session_id=session_id).all()
    for attendance in attendances:
        if attendance.type_of_attendance in attendance_counts:
            attendance_counts[attendance.type_of_attendance] += 1

    school = student.company

    # Generate report for primary school (FrenchSec) 
    if class_.grading_system == 'FrenchSec':
        # Initialize a dictionary to hold composition averages for each student
        student_composition_averages = {}
        sorted_grades = []

        # Compute composition averages for each student in the class
        for other_student in class_.students:
            grades_data_for_student = []
            total_normalized_grades = Decimal(0)
            composition_count = 0  # Count of normalized grades for averaging

            for subject in subjects:
                exams = Exam.query.filter_by(subject_id=subject.id, session_id=session_id, class_id=class_.id, type='composition/examen').all()
                max_grade_value = int(exams[0].max_grade_value) if exams else 1
                
                # Get the grades for this student
                grades = Grade.query.filter_by(subject_id=subject.id, session_id=session_id, student_id=other_student.user_id).join(Exam).filter(Exam.id == Grade.exam_id).all()
                composition_grades = [grade for grade in grades if grade.exam.type == 'composition/examen']
                

                # Normalize each grade and sum them
                for grade in composition_grades:
                    normalized_grade = normalize_grade(Decimal(grade.value), max_grade_value, class_.grading_system)
                    total_normalized_grades += normalized_grade
                    grades_data_for_student.append({
                        'subject': subject.name,
                        'value': grade.value,
                        'normalized_value': normalized_grade
                    })
                    composition_count += 1 


            # Calculate the final composition average on a 1-10 scale for the student
            if composition_count > 0:
                final_composition_avg = total_normalized_grades / composition_count
            else:
                final_composition_avg = Decimal(0)

            # Store the final composition average
            student_composition_averages[other_student.user_id] = final_composition_avg
            sorted_grades.append((other_student.user_id, final_composition_avg, grades_data_for_student))

        sorted_grades.sort(key=lambda x: x[1], reverse=True)

        # Determine rank and create output for the main student
        for index, (student_id, comp_avg, data) in enumerate(sorted_grades):
            rank = index + 1
            rank_label = get_rank_label(rank, student.user.gender)

            if student_id == student.user_id:
                appreciation = get_appreciation_frenchSec(final_composition_avg)

                return {
                    'school_name': school.title,
                    'school_logo_url': school.logo_url,
                    'school_address': school.location,
                    'school_phone': school.phone_number,
                    'school_email': school.email,
                    'student': student,
                    'session': session,
                    'grades_data': data,
                    'gpa':final_composition_avg.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                    'composition_avg': final_composition_avg.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                    'rank': rank,
                    'rank_label': rank_label,
                    'qr_code_url': qr_code_url,
                    'appreciation': appreciation,
                    'report_url': url_for('promote.view_student_report_fr', token=report_token, _external=True)
                }

    # Generate report for middle/high school
    else:
        return {
            'school_name': school.title,
            'school_logo_url': school.logo_url,
            'school_address': school.location,
            'school_phone': school.phone_number,
            'school_email': school.email,
            'student': student,
            'session': session,
            'grades_data': grades_data,
            'gpa': overall_gpa,
            'rank': rank_label,
            'lowest_avg': lowest_avg,
            'highest_avg': highest_avg,
            'class_avg': class_avg,
            'total_weight': total_weight,
            'weighted_average': total_weighted_average,
            'total_weighted_average': total_weighted_average.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
            'total_class_avg': total_class_avg.quantize(Decimal('0.01'), rounding=ROUND_DOWN),
            'total_composition_avg': total_composition_avg,
            'attendance_counts': attendance_counts,
            'qr_code_url': qr_code_url,
            'report_url': url_for('promote.view_student_report_fr', token=report_token, _external=True)
        }


def get_appreciation(average):
    if average >= 16:
        return "Excellent"
    elif average >= 14:
        return "Très Bien"
    elif average >= 12:
        return "Bien"
    elif average >= 10:
        return "Assez Bien"
    else:
        return "Insuffisant"


def get_appreciation_frenchSec(composition_avg):
    """
    Provide an appreciation based on the student's composition average on a 1-10 scale.

    Args:
    - composition_avg (Decimal): The composition average of the student normalized on a 1-10 scale.

    Returns:
    - str: A string representing the appreciation in French.
    """
    if composition_avg >= 9:
        return "Excellent"
    elif composition_avg >= 8:
        return "Très bien"
    elif composition_avg >= 7:
        return "Bien"
    elif composition_avg >= 6:
        return "A.Bien"
    elif composition_avg >= 5:
        return "Passable"
    elif composition_avg >= 4:
        return "Mediocre"
    elif composition_avg >= 3:
        return "Nul"
    elif composition_avg >= 2:
        return "Très Nul"
    else:
        return "Peut mieux faire"


def get_previous_sessions(academic_year_id, current_start_date):
    return (
        Session.query
        .filter(Session.academic_year_id == academic_year_id)
        .filter(Session.start_date < current_start_date)
        .all()
    )


def get_all_students_gpas_in_class(class_id):
    students_with_gpas = []

    # Query to get all students in the specified class
    students = Student.query.filter_by(class_id=class_id).all()

    # Loop through each student to compute their GPA
    for student in students:
        # Assuming user_id is the identifier to compute the GPA
        user_id = student.user_id  
        previous_sessions = get_previous_sessions()  # Function to get previous sessions
        annual_gpa, _ = calculate_annual_gpa_and_rank(user_id, previous_sessions)  # Use the provided GPA calculation function
        students_with_gpas.append((student.user.full_name, annual_gpa))  # Append student name and GPA

    return students_with_gpas


def calculate_annual_gpa_and_rank(user_id, previous_sessions):
    gpas = []
    
    for session in previous_sessions:
        report_data = compute_student_report_fr(user_id, session.id)
        gpas.append(report_data['gpa'])

    if gpas:
        annual_gpa = sum(gpas) / len(gpas)
    else:
        annual_gpa = 0.0

    all_students = get_all_students_gpas_in_class(user_id) 
    all_students.sort(key=lambda x: x[1], reverse=True) 
    # Determine rank
    rank = 1 + sum(1 for _, gpa in all_students if gpa > annual_gpa)

    return annual_gpa, rank

