from datetime import datetime
from ... import db
from ...models.school.classroom import Class
from ...models.school.grade import Grade

def check_and_promote_students():
    current_date = datetime.utcnow().date()
    session_end_date = datetime(current_date.year, 6, 30).date()  # Example session end date: June 30th

    if current_date == session_end_date:
        classes = Class.query.all()
        for class_ in classes:
            for student in class_.students:
                gpa = calculate_gpa(student)
                if gpa >= class_.passing_gpa:
                    promote_student(student, class_.next_level)
                elif gpa < class_.failing_gpa:
                    retain_student(student, class_.name)

def calculate_gpa(student):
    grades = Grade.query.filter_by(student_id=student.id).all()
    total_points = sum(float(grade.value) for grade in grades)
    gpa = total_points / len(grades) if grades else 0.0
    return gpa

def promote_student(student, next_class_name):
    next_class = Class.query.filter_by(name=next_class_name).first()
    if next_class:
        student.class_id = next_class.id
        db.session.commit()

def retain_student(student, current_class_name):
    current_class = Class.query.filter_by(name=current_class_name).first()
    if current_class:
        student.class_id = current_class.id
        db.session.commit()
