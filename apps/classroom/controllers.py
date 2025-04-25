from . import classroom
from flask_login import login_required, current_user
from ..decorators import school_it_admin_required, teacher_required
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import render_template, request, jsonify, abort
from ..models.general.company import Company
from ..models.school.classroom import Class
from ..models.school.session import Session
from ..models.school.subject import Subject
from ..models.school.teacher import Teacher
from ..models.school.exam import Exam
from ..models.school.student import Student
from ..models.general.role import Role
from ..models.school.grade import Grade
from ..models.school.subject_teacher import subject_teacher
from ..models.general.user import User
from ..models.school.class_subject import class_subject
from ..models.school.academic_year import AcademicYear
from ..models.school.section import Section
from ..models.school.attendance import Attendance
from ..models.school.class_teacher import class_teacher
from ..models.engineering.pipeline import Pipeline
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from .. import db
from flask_babel import gettext as _

@classroom.route("/manage_classes/<int:company_id>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
@school_it_admin_required
def manage_classes(company_id):
    company = Company.query.get_or_404(company_id)
    page = request.args.get('page', 1, type=int)

    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
        except Exception as e:
            return jsonify({"success": False, "message": "Invalid JSON payload"}), 400

        name = data.get('name')
        next_level = data.get('next_level')
        tuition = data.get('tuition')
        currency = data.get('currency', 'USD')
        installments = data.get('installments')
        passing_gpa = data.get('passing_gpa')
        session_id = data.get('session_id')
        grading_system = data.get('grading_system')
        section_id = data.get('section_id')

        if not name or not next_level or not tuition or not passing_gpa or not grading_system:
            return jsonify(
                {
                    "success": False, 
                    'title': _('Erreur'),
                    "message": _('Tous les champs requis doivent être complétés'),
                    'confirmButtonText': _('confirmButtonText')
                }
            ), 400

        new_class = Class(
            name=name,
            next_level=next_level,
            tuition=tuition,
            currency=currency,
            installments=installments,
            passing_gpa=passing_gpa,
            session_id=session_id,
            grading_system=grading_system,
            company_id=company_id,
            section_id=section_id
        )
        db.session.add(new_class)
        db.session.commit()
        return jsonify(
            {
                'title': _('Classe ajoutée'),
                "success": True, 
                "message": _("Classe créée avec succès!"),
                "confirmButtonText": _("OK")
            }
        )
    
    elif request.method == 'PUT':
        data = request.form
        updated = []

        for key, value in data.items():
            if key.startswith(('name_', 'next_level_', 'tuition_', 'currency_', 'installments_', 'passing_gpa_', 'session_id_', 'grading_system_')):
                try:
                    class_id = int(key.split('_')[1])
                except (IndexError, ValueError):
                    continue

                field = key.split('_')[0]
                class_obj = Class.query.get(class_id)
                
                if not class_obj:
                    continue
                
                if field == 'name':
                    class_obj.name = value
                elif field == 'next_level':
                    class_obj.next_level = value
                elif field == 'tuition':
                    class_obj.tuition = float(value)
                elif field == 'currency':
                    class_obj.currency = value
                elif field == 'installments':
                    class_obj.installments = int(value)
                elif field == 'passing_gpa':
                    class_obj.passing_gpa = float(value)
                elif field == 'session_id':
                    class_obj.session_id = int(value)
                elif field == 'grading_system':
                    class_obj.grading_system = value
                
                updated.append(class_id)

        db.session.commit()
        return jsonify(
            {
                "success": True, 
                "updated_ids": updated,
                "title": _('Mise à jour effectuée'),
                "message": _('Classe mise à jour avec succès'),
                "confirmButtonText": _('OK')
            }
        )

    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        class_id = data.get('id')
        class_obj = Class.query.get_or_404(class_id)

        db.session.delete(class_obj)
        db.session.commit()
        return jsonify(
            {
                "success": True, 
                "title": _("Supprimée"),
                "message": _("Classe supprimée"),
                "confirmButtonText": _("OK")
            }
        )

    else:
        classes = Class.query.filter_by(company_id=company_id).paginate(per_page=10)

        next_levels = Class.query.filter_by(company_id=company.id).distinct(Class.next_level).all()

        active_academic_year = AcademicYear.query.filter_by(company_id=company.id, active=1).first()
        if active_academic_year:
            sessions = Session.query.filter_by(academic_year_id=active_academic_year.id).all()
        else:
            sessions = []

        sections = Section.query.filter_by(company_id=company.id).all()

        sessions = Session.query.filter_by(company_id=company.id, ).all()
        return render_template(
            'dashboard/@support_team/school/manage_classroom.html',
            company=company,
            classes=classes.items,
            pagination=classes,
            sessions=sessions,
            sections=sections,
            next_levels=[level.next_level for level in next_levels]
        )
    
    
@classroom.route('/manage_subjects/<int:company_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def manage_subjects(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        weight = data.get('weight', 1)
        teacher_id = data.get('teacher')
        class_ids = data.get('classes', [])

        if not name:
            return jsonify({'message': 'Le nom de la matière est requis.'}), 400

        # Check for duplicate subject name within the same class
        for class_id in class_ids:
            existing_subject = db.session.query(Subject).join(class_subject).filter(
                class_subject.c.class_id == class_id,
                Subject.name == name,
                Subject.company_id == company_id
            ).first()

            if existing_subject:
                return jsonify({'message': f'Une matière avec le nom "{name}" existe déjà dans la classe.'}), 400

        new_subject = Subject(name=name, weight=weight, company_id=company_id)
        db.session.add(new_subject)
        db.session.commit()

        if teacher_id:
            teacher = Teacher.query.get(teacher_id)
            if teacher:
                new_subject.teachers.append(teacher)
                for class_id in class_ids:
                    classroom = Class.query.get(class_id)
                    if classroom:
                        if not db.session.query(class_subject).filter_by(class_id=classroom.id, subject_id=new_subject.id).first():
                            db.session.execute(class_subject.insert().values(class_id=classroom.id, subject_id=new_subject.id))

                        # Assign the new subject to all students in the classroom/major
                        students_in_class = Student.query.filter_by(class_id=class_id).all()
                        for student in students_in_class:
                            if new_subject not in student.subjects:
                                student.subjects.append(new_subject)

                        classroom.teachers.append(teacher)

        db.session.commit()

        return jsonify(
            {
                'title': _('Nouvelle matière ajoutée'),
                'message': _('Matière créée avec succès.'), 
                'subject': 
                {
                    'id': new_subject.id, 
                    'name': new_subject.name
                }
            }
        ), 201


    if request.method == 'PUT':
        data = request.get_json()
        subject_id = data.get('id')
        name = data.get('name')
        weight = data.get('weight', 1)
        teacher_id = data.get('teacher')
        class_ids = data.get('classes', [])

        if not subject_id or not name:
            return jsonify(
                {
                    'title': _('Error'),
                    'message': _('ID et nom de la matière sont requis.')
                }
            ), 400

        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify(
                {
                    'title': _('Error'),
                    'message': _('Matière non trouvée.')
                }
            ), 404

        # Check for duplicate subject name within the same class when updating
        for class_id in class_ids:
            existing_subject = db.session.query(Subject).join(class_subject).filter(
                class_subject.c.class_id == class_id,
                Subject.name == name,
                Subject.company_id == company_id,
                Subject.id != subject_id  # Exclude the current subject from the check
            ).first()

            if existing_subject:
                return jsonify({'message': f'Une matière avec le nom "{name}" existe déjà dans la classe.'}), 400

        subject.name = name
        subject.weight = weight

        if teacher_id:
            teacher = Teacher.query.get(teacher_id)
            if teacher:
                subject.teachers = [teacher]
                for class_id in class_ids:
                    classroom = Class.query.get(class_id)
                    if classroom:
                        if not db.session.query(class_subject).filter_by(class_id=classroom.id, subject_id=subject.id).first():
                            db.session.execute(class_subject.insert().values(class_id=classroom.id, subject_id=subject.id))
                        if teacher not in classroom.teachers:
                            classroom.teachers.append(teacher)

        db.session.commit()
        return jsonify(
            {
                'title': _('Mise à jour effectuée'),
                'message': _('Matière mise à jour avec succès.'), 
                'subject': {
                    'id': subject.id, 
                    'name': subject.name
                }
            }
        ), 200


    if request.method == 'DELETE':
        data = request.get_json()
        subject_id = data.get('id')
        if not subject_id:
            return jsonify(
                {
                    'title': _('Erreur!'),
                    'message': _('ID de la matière est requis.')
                }
            ), 400

        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify(
                {
                    'title': _('Erreur!'),
                    'message': _( 'Matière non trouvée.')
                }
            ), 404

        db.session.execute(class_subject.delete().where(class_subject.c.subject_id == subject_id))
        db.session.delete(subject)
        db.session.commit()
        return jsonify(
            {
                'title': _('Supprimé'),
                'message': _('Matière supprimée')
            }
        ), 200

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        pagination = Subject.query.filter_by(company_id=company_id).paginate(page=page, per_page=10, error_out=False)
        subjects = pagination.items
        teachers = Teacher.query.filter_by(company_id=company_id).all()
        classes = Class.query.filter_by(company_id=company_id).all()

        return render_template(
            'dashboard/@support_team/school/manage_subject.html',
            subjects=subjects,
            company=company,
            pagination=pagination,
            classes=classes,
            teachers=teachers
        )

@classroom.route('/manage_grades/<int:company_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@teacher_required
def manage_grades(company_id):
    company = Company.query.get_or_404(company_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    if request.method == 'PUT':
        data = request.get_json()
        try:
            for item in data:
                student = Student.query.filter_by(user_id=item['student_id']).first_or_404()
                user_id = student.user_id

                existing_grade = Grade.query.filter_by(
                    student_id=user_id,
                    subject_id=item['subject_id'],
                    exam_id=item['exam_id'],
                    session_id=item['session_id']
                ).first()

                if existing_grade:
                    existing_grade.value = item['value']
                else:
                    new_grade = Grade(
                        value=item['value'],
                        student_id=user_id,
                        subject_id=item['subject_id'],
                        teacher_id=current_user.id,
                        exam_id=item['exam_id'],
                        session_id=item['session_id']
                    )
                    db.session.add(new_grade)

            db.session.commit()
            return jsonify(
                {
                    'title': _('Sauvegarde effectuée'),
                    'message': _('Les notes ont été bien sauvegardées'),
                    'confirmButtonText': _('OK')
                }
            ), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify(
                {
                    'title': _('Erreur'),
                    'message': _('Une erreur est survenue lors de la mise à jour des notes')
                }
            ), 400

    elif request.method == 'DELETE':
        data = request.get_json()
        for grade_id in data['ids']:
            grade = Grade.query.get_or_404(grade_id)
            if grade.teacher_id == current_user.id:
                db.session.delete(grade)
            else:
                return jsonify({'message': 'Unauthorized'}), 403
        db.session.commit()
        return jsonify({'message': 'Grades deleted successfully'}), 200

    else:
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        exams = Exam.query.filter_by(teacher_id=current_user.id).all()
        sessions = Session.query.join(AcademicYear).filter(
            Session.company_id == company.id,
            AcademicYear.active == True
        ).all()

        classes = Class.query.join(Class.teachers).filter(Teacher.id == teacher.id).all()
        subjects = Subject.query.join(Subject.teachers).filter(Teacher.id == teacher.id).all()

        class_id = request.args.get('class_id')

        subject_id = request.args.get('subject_id')
        
        if subject_id:
            exams = Exam.query.filter_by(teacher_id=current_user.id, subject_id=subject_id).all()
        else:
            exams = Exam.query.filter_by(teacher_id=current_user.id).all()

        exam_id = request.args.get('exam_id')
        session_id = request.args.get('session_id')

        query = Student.query.filter(Student.class_id == Class.id, Class.company_id == company.id)

        if class_id:
            query = query.filter(Student.class_id == class_id)

        if session_id:
            query = query.filter(Student.session_id == session_id)

        if subject_id:
            query = query.join(Student.subjects).filter(Subject.id == subject_id)

        if exam_id:
            query = query.join(Student.exams).filter(Exam.id == exam_id)

        students = query.distinct().paginate(page=page, per_page=per_page, error_out=False)
        student_ids = [student.user_id for student in students.items]

        grades_query = Grade.query.filter(
            Grade.student_id.in_(student_ids),
            Grade.teacher_id == current_user.id,
            Grade.subject_id == subject_id,
            Grade.exam_id == exam_id,
            Grade.session_id == session_id
        )

        grades = grades_query.all()

        total_pages = students.pages

        return render_template(
            'dashboard/@support_team/school/manage_grades.html',
            company=company,
            exams=exams,
            sessions=sessions,
            classes=classes,
            subjects=subjects,
            students=students.items,
            grades=grades,
            current_page=page,
            total_pages=total_pages
        )

@classroom.route('/manage_attendance/<int:company_id>', methods=['GET', 'PUT'])
@login_required
@teacher_required
def manage_attendance(company_id):
    company = Company.query.get_or_404(company_id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Fetch classes taught by the teacher in the specified school
    classes = Class.query.join(Class.teachers).filter(
        Teacher.id == teacher.id,
        Class.company_id == company.id
    ).all()

    # Fetch filters from request args
    class_id = request.args.get('class_id')
    session_id = request.args.get('session_id')
    date_filter = request.args.get('date', None)
    date_filter = datetime.strptime(date_filter, "%Y-%m-%d").date() if date_filter else None

    students = []
    sessions = []
    students_pagination = None
    page = request.args.get('page', 1, type=int)  # Get the current page number, default to 1
    per_page = 10  # Number of students per page

    if class_id:
        # Fetch active academic year for the company
        active_academic_year = AcademicYear.query.filter_by(company_id=company_id, active=True).first()

        if active_academic_year:
            # Fetch sessions associated with the selected class and active academic year
            sessions = Session.query.filter_by(
                academic_year_id=active_academic_year.id
            ).all()
        
        if session_id and date_filter:
            # Fetch students for the given class and session, based on the date
            students_query = Student.query.join(User).filter(
                Student.class_id == class_id,
                Student.session_id == session_id
            ).order_by(User.last_name)

            students_pagination = students_query.paginate(page=page, per_page=per_page)
            students = students_pagination.items  # Get the students for the current page
            
            # Fetch and attach attendance data for each student
            for student in students:
                attendance_record = Attendance.query.filter_by(
                    student_id=student.id,
                    date=date_filter,
                    session_id=session_id
                ).first()
                
                # If an attendance record exists, attach its data to the student object
                if attendance_record:
                    student.attendance_type = attendance_record.type_of_attendance
                    student.attendance_number = attendance_record.number
                else:
                    student.attendance_type = None
                    student.attendance_number = 1

    # Handle PUT request to update or create attendance records
    if request.method == 'PUT':
        data = request.get_json()
        try:
            for item in data:
                student_id = item['student_id']
                attendance_record = Attendance.query.filter_by(
                    student_id=student_id,
                    date=date_filter,
                    session_id=session_id
                ).first()

                if attendance_record:
                    attendance_record.type_of_attendance = item['type']
                    attendance_record.number = item.get('number', 1)
                else:
                    new_attendance = Attendance(
                        date=date_filter,
                        type_of_attendance=item['type'],
                        number=item.get('number', 1),
                        student_id=student_id,
                        session_id=session_id
                    )
                    db.session.add(new_attendance)

            db.session.commit()
            return jsonify(
                {
                    'title': _('Sauvegarde effectuée'),
                    'message': _('Les notes disciplinaires ont bien été mises à jour'),
                    'confirmButtonText': _('OK')
                }
            ), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify(
                {
                    'title': _('Erreur'),
                    'message': _('Erreur lors de la mise à jour')
                }
            ), 400

    return render_template(
        'dashboard/@support_team/school/manage_attendance.html',
        company=company,
        classes=classes,
        students=students,
        students_pagination=students_pagination if session_id and date_filter else None,
        date_filter=date_filter,
        session_id=session_id,
        class_id=class_id,
        sessions=sessions
    )


@classroom.route('/manage_exams/<int:company_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@teacher_required
def manage_exams(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            date = data.get('examDate')
            exam_class_id = data.get('examClass')
            
            # Create the new exam
            new_exam = Exam(
                name=data.get('examName'),
                type=data.get('examType'),
                max_grade_value=data.get('examGradeValue'),
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                subject_id=data.get('examSubject'),
                class_id=exam_class_id,
                session_id=data.get('examSession'),
                company_id=company.id,
                teacher_id=current_user.id
            )
            db.session.add(new_exam)
            db.session.commit()

            # Fetch all students in the same class
            students_in_class = Student.query.filter_by(class_id=exam_class_id).all()
            
            # Associate the exam with all students in the class
            for student in students_in_class:
                student.exams.append(new_exam)
            
            db.session.commit()

            return jsonify({"message": _("Examen ajouté"), "confirmButtonText" : _('OK')}), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e), "confirmButtonText": _('OK')}), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json(force=True)
            exam_id = data.get('examId')
            exam = Exam.query.get_or_404(exam_id)
            exam.type = data.get('examType')
            exam.date = datetime.strptime(data.get('examDate'), '%Y-%m-%d').date()
            exam.subject_id = data.get('examSubject')
            exam.class_id = data.get('examClass')
            exam.session_id = data.get('examSession')
            exam.max_grade_value = data.get('examGradeValue')
            db.session.commit()
            return jsonify({"message": _("Examen mis à jour avec succès"), "confirmButtonText": _("OK")}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e), "confirmButtonText": _('OK')}), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json(force=True)
            exam_id = data.get('examId')
            exam = Exam.query.get_or_404(exam_id)
            db.session.delete(exam)
            db.session.commit()
            return jsonify({"message": _("Examen supprimé avec succès"), "confirmButtonText": _('OK')}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    else:
        selected_session = request.args.get('session_id', type=int)
        selected_subject = request.args.get('subject_id', type=int)

        active_academic_year = AcademicYear.query.filter_by(company_id=company.id, active=True).first()
        sessions = Session.query.filter_by(company_id=company.id, academic_year_id=active_academic_year.id).all()

        # Fetch teacher and associated classes and subjects
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if teacher:
            subjects = Subject.query.join(Subject.teachers).filter(Teacher.id == teacher.id).all()
            classes = Class.query.join(Class.teachers).filter(Teacher.id == teacher.id).all()
        else:
            subjects = []
            classes = []

        exams = Exam.query.filter_by(company_id=company.id, teacher_id=current_user.id)

        if selected_session:
            exams = exams.filter_by(session_id=selected_session)
        if selected_subject:
            exams = exams.filter_by(subject_id=selected_subject)

        exams = exams.all()

        subject_dict = {subject.id: subject.name for subject in subjects}
        class_dict = {cls.id: cls.name for cls in classes}
        session_dict = {session.id: session.name for session in sessions}

        return render_template(
            'dashboard/@support_team/school/manage_exam.html',
            company=company,
            exams=exams,
            sessions=sessions,
            subjects=subjects,
            classes=classes,
            subject_dict=subject_dict,
            class_dict=class_dict,
            session_dict=session_dict,
            selected_session=selected_session,
            selected_subject=selected_subject
        )


@classroom.route('/manage_pipelines/<int:company_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_pipelines(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'GET':
        users = User.query.join(Role).filter(
            User.company_id == company_id,
            Role.position.in_(['agent'])
        ).all()
        pipelines = Pipeline.query.filter_by(company_id=company.id).all()
        return render_template(
            'dashboard/@support_team/engineering/pipelines.html',
            pipelines=pipelines,
            users=users,
            company=company
        )
    if request.method == 'POST':
        data = request.form
        pipeline_name = data.get('pipeline_name')
        pipeline_identifier = data.get('pipeline_identifier')
        pipeline_type = data.get('pipeline_type')
        pipeline_status = data.get('pipeline_status')
        pipeline_location = data.get('pipeline_location')

        existing_pipeline = Pipeline.query.filter_by(pipeline_name=pipeline_name).first()

        if existing_pipeline:
            return jsonify(
                { 
                    'success': False,
                    'title': _('Erreur'),
                    'message': _('Cette station existe déja, veuillez changer de nom') 
                }
            )
        new_pipeline = Pipeline(
            pipeline_name=pipeline_name,
            pipeline_identifier=pipeline_identifier,
            pipeline_type=pipeline_type,
            pipeline_status=pipeline_status,
            pipeline_location=pipeline_location,
            company_id=company.id
        )


        db.session.add(new_pipeline)

        db.session.commit()

        return jsonify(
            {
                'success': True,
                'title': _(f'{pipeline_name} ajoutée'),
                'message': _('La station a été correctement ajoutée')
            }
        )
    


