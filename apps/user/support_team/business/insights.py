from datetime import datetime, timedelta
from sqlalchemy import func, extract
from .... import db
from ....models.shipping.authorization import Authorization 
from ....models.shipping.purchase import Purchase
from ....models.general.user import User
from ....models.general.role import Role
from ....models.school.student import Student
from ....models.school.grade import Grade
from ....models.school.attendance import Attendance
from ....models.school.session import Session
from ....models.school.academic_year import AcademicYear
from ....models.school.exam import Exam
from ....models.school.book import Book
from ....models.school.book_loan import BookLoan
from ....models.school.installment import Installment
from ....models.school.expense import Expense
from ....models.general.company import Company
from ....models.general.file import File
from ....models.general.folder import Folder
from ....models.shipping.product import Product
from ....models.general.article import Article
from ....models.general.audiobook import AudioBook
from ....models.school.book import Book
from ....models.general.invoice import Invoice
from ....models.school.section import Section
from ....models.general.company_expense import CompanyExpense
from ....models.school.subject import Subject
from ....models.school.classroom import Class
from ....models.school.teacher import Teacher
from ....models.general.job import Job
from ....models.general.note import Note
from ....models.general.marketingcampaign import MarketingCampaign
from ....models.general.employee import Employee
from ....models.general.project import Project
from ....models.school.finance import Finance
from flask_login import current_user
from sqlalchemy.orm import aliased
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_weekly_service_fees(company_id):
    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=7)

    logger.debug(f"Calculating service fees for the week from {start_of_week} to {end_of_week} for company {company_id}")

    current_week_authorization_fees = db.session.query(
        func.sum(Authorization.service_fees)
    ).filter(
        Authorization.date >= start_of_week,
        Authorization.date < end_of_week,
        Authorization.company_id == company_id
    ).scalar()

    current_week_purchase_fees = db.session.query(
        func.sum(Purchase.service_fees)
    ).filter(
        Purchase.start_check >= start_of_week,
        Purchase.start_check < end_of_week,
        Purchase.company_id == company_id
    ).scalar()

    current_week_fees = (current_week_authorization_fees or 0) + (current_week_purchase_fees or 0)

    previous_week_start = start_of_week - timedelta(days=7)
    previous_week_end = start_of_week

    logger.debug(f"Calculating service fees for the previous week from {previous_week_start} to {previous_week_end} for company {company_id}")

    previous_week_authorization_fees = db.session.query(
        func.sum(Authorization.service_fees)
    ).filter(
        Authorization.date >= previous_week_start,
        Authorization.date < previous_week_end,
        Authorization.company_id == company_id
    ).scalar()

    previous_week_purchase_fees = db.session.query(
        func.sum(Purchase.service_fees)
    ).filter(
        Purchase.start_check >= previous_week_start,
        Purchase.start_check < previous_week_end,
        Purchase.company_id == company_id
    ).scalar()

    previous_week_fees = (previous_week_authorization_fees or 0) + (previous_week_purchase_fees or 0)

    return current_week_fees, previous_week_fees


def calculate_percentage_difference(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

def get_weekly_financial_summary(company_id):
    current_week_fees, previous_week_fees = get_weekly_service_fees(company_id)
    percentage_difference = calculate_percentage_difference(current_week_fees, previous_week_fees)

    logger.debug(f"Weekly financial summary for company {company_id}: current_week_fees={current_week_fees}, previous_week_fees={previous_week_fees}, percentage_difference={percentage_difference}")

    return {
        'current_week_fees': current_week_fees,
        'previous_week_fees': previous_week_fees,
        'percentage_difference': percentage_difference,
        'status': 'gain' if percentage_difference > 0 else 'loss'
    }


def get_user_role_count(company_id):
    user_role = Role.query.filter_by(position='customer').first()
    if not user_role:
        return 0, 0

    today = datetime.utcnow()
    start_of_current_month = datetime(today.year, today.month, 1)
    start_of_previous_month = (start_of_current_month - timedelta(days=1)).replace(day=1)
    end_of_previous_month = start_of_current_month - timedelta(days=1)

    logger.debug(f"Calculating user role count for role 'User' in company {company_id}")

    current_month_count = db.session.query(func.count(User.id)).filter(
        User.role_id == user_role.id,
        User.member_since >= start_of_current_month,
        User.company_id == company_id
    ).scalar()

    previous_month_count = db.session.query(func.count(User.id)).filter(
        User.role_id == user_role.id,
        User.member_since >= start_of_previous_month,
        User.member_since < start_of_current_month,
        User.company_id == company_id
    ).scalar()

    return current_month_count, previous_month_count


def get_monthly_user_summary(company_id):
    current_count, previous_count = get_user_role_count(company_id)
    percentage_difference = calculate_percentage_difference(current_count, previous_count)

    logger.debug(f"Monthly user summary for company {company_id}: current_count={current_count}, previous_count={previous_count}, percentage_difference={percentage_difference}")

    return {
        'current_count': current_count,
        'previous_count': previous_count,
        'percentage_difference': percentage_difference,
        'status': 'gain' if percentage_difference > 0 else 'loss'
    }


def get_daily_client_count(company_id):
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    logger.debug(f"Calculating daily client count for today: {today} and yesterday: {yesterday} for company {company_id}")

    today_authorizations = db.session.query(func.count(Authorization.id)).filter(
        func.date(Authorization.date) == today,
        Authorization.company_id == company_id
    ).scalar()

    today_purchases = db.session.query(func.count(Purchase.id)).filter(
        func.date(Purchase.start_check) == today,
        Purchase.company_id == company_id
    ).scalar()

    yesterday_authorizations = db.session.query(func.count(Authorization.id)).filter(
        func.date(Authorization.date) == yesterday,
        Authorization.company_id == company_id
    ).scalar()

    yesterday_purchases = db.session.query(func.count(Purchase.id)).filter(
        func.date(Purchase.start_check) == yesterday,
        Purchase.company_id == company_id
    ).scalar()

    today_clients = (today_authorizations or 0) + (today_purchases or 0)
    yesterday_clients = (yesterday_authorizations or 0) + (yesterday_purchases or 0)

    return today_clients, yesterday_clients


def get_daily_client_summary(company_id):
    today_clients, yesterday_clients = get_daily_client_count(company_id)
    percentage_difference = calculate_percentage_difference(today_clients, yesterday_clients)

    logger.debug(f"Daily client summary for company {company_id}: today_clients={today_clients}, yesterday_clients={yesterday_clients}, percentage_difference={percentage_difference}")

    return {
        'today_clients': today_clients,
        'yesterday_clients': yesterday_clients,
        'percentage_difference': percentage_difference,
        'status': 'gain' if percentage_difference > 0 else 'loss'
    }


def get_user_invoices(user_id):
    purchases = Purchase.query.filter_by(user_id=user_id, closed=False).all()
    authorizations = Authorization.query.filter_by(user_id=user_id, granted=False).all()

    logger.debug(f"Getting invoices for user_id: {user_id}")

    invoices = []
    for purchase in purchases:
        invoices.append({
            'id': purchase.id,
            'title': purchase.title,
            'amount': purchase.service_fees
        })
    for authorization in authorizations:
        invoices.append({
            'id': authorization.id,
            'title': 'Demande de procuration',
            'amount': authorization.service_fees
        })
    return invoices


def count_all_students(company_id):
    try:
        # Query the Student model to count all students for a specific company
        student_count = Student.query.filter_by(company_id=company_id).count()
        return student_count
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error counting students: {e}")
        return None


def calculate_student_count_percentage_difference(company_id):
    try:
        # Calculate dates for today and yesterday
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Count the number of students who joined today and yesterday for the specific company
        today_count = Student.query.filter_by(company_id=company_id).filter(
            Student.user.has(User.member_since.between(today, today))
        ).count()

        yesterday_count = Student.query.filter_by(company_id=company_id).filter(
            Student.user.has(User.member_since.between(yesterday, yesterday))
        ).count()
        
        # Calculate percentage difference
        if yesterday_count == 0:
            percentage_difference = 0 if today_count == 0 else 100
        else:
            percentage_difference = ((today_count - yesterday_count) / yesterday_count) * 100
        
        return round(percentage_difference, 2)
    except Exception as e:
        print(f"Error calculating percentage difference: {e}")
        return None



def calculate_student_data_size(company_id):
    try:
        # Size of student-related text fields (first_name, last_name, email, address)
        student_size = db.session.query(
            func.sum(
                func.length(User.first_name) +
                func.length(User.last_name) + 
                func.length(User.email) +
                func.length(User.address)
            ).label('student_size')
        ).join(Student, Student.user_id == User.id).filter(Student.company_id == company_id).scalar() or 0

        # Handle the size of grade columns
        # If Grade.value is numeric, we can't use length(), so just add its byte size
        grade_size = db.session.query(
            func.sum(
                func.coalesce(func.length(Grade.value.cast(db.String)), 0)
            ).label('grade_size')
        ).join(Student, Grade.student_id == Student.user_id).filter(Student.company_id == company_id).scalar() or 0

        # Size of attendance-related text fields (e.g., type_of_attendance)
        attendance_size = db.session.query(
            func.sum(
                func.length(Attendance.type_of_attendance)
            ).label('attendance_size')
        ).join(Student, Attendance.student_id == Student.user_id).filter(Student.company_id == company_id).scalar() or 0

        # Sum up the sizes
        total_size = student_size + grade_size + attendance_size

        return total_size
    except Exception as e:
        print(f"Error calculating data size: {e}")
        return None

    

def count_school_sessions(company_id):
    try:
        # Query the Session model to count all sessions for a specific school
        session_count = Session.query.filter_by(company_id=company_id).count()
        return session_count
    except Exception as e:
        print(f"Error counting sessions: {e}")
        return None
    
def get_academic_year_for_session(company_id):
    try:
        # Query to find the most recent session for the specific company
        session = Session.query.filter_by(company_id=company_id).order_by(Session.start_date.desc()).first()
        
        if session:
            # Get the academic year associated with this session
            academic_year = AcademicYear.query.filter_by(id=session.academic_year_id).first()
            return academic_year.name if academic_year else None
        return None
    except Exception as e:
        print(f"Error retrieving academic year: {e}")
        return None

def get_exams_for_teacher(company_id):
    try:
        # Query to find all the exams created by a teacher
        exams = Exam.query.filter_by(
            teacher_id=current_user.id
        ).count()
        return exams
    except Exception as e:
        print(f"Error counting exams created by the teacher: {e}")
        return None


def get_classes_for_teacher(company_id):
    """
    implement the logic to get the number
    of classes for a teacher
    """
    pass

def get_students_number(company_id):
    """
    implement the logic to get the number
    of students in classes where the teacher
    teach
    """
    pass

def get_students_number(company_id):
    """
    implement the logic to get the number
    of students in classes where the teacher
    teach
    """
    pass



def get_student_session_avg(company_id):
    """
    implement the logic to get 
    the avg grade of all students
    """
    pass

def get_number_of_books(company_id):
    """
    Get the total number of books for a specific company.
    
    Args:
        company_id (int): The ID of the company.
    
    Returns:
        int: The number of books associated with the company.
    """
    return Book.query.filter_by(company_id=company_id).count()


def get_number_of_book_loans(company_id):
    """
    Get the total number of book loans for a specific company.
    
    Args:
        company_id (int): The ID of the company.
    
    Returns:
        int: The number of book loans associated with the company.
    """
    return BookLoan.query.join(Book).filter(Book.company_id == company_id).count()


def last_month_start_date():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_month = first_day_of_current_month - timedelta(days=1)
    return last_month.replace(day=1)

def last_month_end_date():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_last_month


# Function to calculate the total amount received by students during the latest session
def calculate_total_versed_by_students(company_id):
    total = db.session.query(db.func.sum(Installment.amount)).filter(
        Installment.student.has(company_id=company_id)
    ).scalar()
    
    return total or 0  # Return 0 if total is None

# Function to calculate total expenses (from invoices and wages)
def calculate_total_expenses(company_id):
    total = db.session.query(db.func.sum(Expense.amount)).filter_by(company_id=company_id).scalar()
    return total or 0  # Return 0 if total is None



def calculate_student_count_percentage_difference(company_id):
    try:
        # Calculate dates for today and yesterday
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Count the number of students who joined today and yesterday for the specific company
        today_count = Student.query.filter_by(company_id=company_id).filter(
            Student.user.has(User.member_since.between(today, today))
        ).count()

        yesterday_count = Student.query.filter_by(company_id=company_id).filter(
            Student.user.has(User.member_since.between(yesterday, yesterday))
        ).count()
        
        # Calculate percentage difference
        if yesterday_count == 0:
            percentage_difference = 0 if today_count == 0 else 100
        else:
            percentage_difference = ((today_count - yesterday_count) / yesterday_count) * 100
        
        return round(percentage_difference, 2)
    except Exception as e:
        print(f"Error calculating percentage difference: {e}")
        return None


def count_all_companies():
    return db.session.query(Company).count()

def count_companies_registered_on(date):
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())

    return db.session.query(Company).filter(Company.registration_date.between(start_date, end_date)).count()

def get_daily_company_summary():
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    current_count = count_companies_registered_on(today)
    previous_count = count_companies_registered_on(yesterday)

    # Avoid division by zero
    percentage_difference = ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else 0

    return {
        'current_count': current_count,
        'previous_count': previous_count,
        'percentage_difference': percentage_difference,
        'status': 'gain' if percentage_difference > 0 else 'loss'
    }


def get_relevant_urls_for_company(company_id):
    """Fetches all relevant file URLs for a company from the database."""
    urls = []

    # Fetching from the 'File' model
    file_entries = File.query.join(Folder).filter(Folder.company_id == company_id).all()
    urls += [file.filepath for file in file_entries]

    # Fetching from the 'Product' model
    product_entries = Product.query.filter_by(company_id=company_id).all()
    urls += [product.product_img_url for product in product_entries if product.product_img_url]
    urls += [product.barcode_url for product in product_entries if product.barcode_url]

    # Fetching from the 'Purchase' model
    purchase_entries = Purchase.query.filter_by(company_id=company_id).all()
    urls += [purchase.qr_code_url for purchase in purchase_entries if purchase.qr_code_url]
    urls += [purchase.barcode_url for purchase in purchase_entries if purchase.barcode_url]

    # Fetching from the 'User' model
    user_entries = User.query.filter_by(company_id=company_id).all()
    urls += [user.profile_picture_url for user in user_entries if user.profile_picture_url]

    # Fetching from the 'Article' model
    article_entries = Article.query.filter_by(company_id=company_id).all()
    urls += [article.article_img_url for article in article_entries if article.article_img_url]

    # Fetching from the 'Book' model
    book_entries = Book.query.filter_by(company_id=company_id).all()
    urls += [book.image_url for book in book_entries if book.image_url]
    urls += [book.ebook_url for book in book_entries if book.ebook_url]

    # Fetching from the 'AudioBook' model
    audiobook_entries = AudioBook.query.filter_by(company_id=company_id).all()
    urls += [audiobook.audio_url for audiobook in audiobook_entries if audiobook.audio_url]

    # Fecthing from the 'Invoice' model
    invoice_entries = Invoice.query.filter_by(company_id=company_id).all()
    urls += [invoice.qr_code_url for invoice in invoice_entries if invoice.qr_code_url]    

    return urls


def get_data_size_for_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        raise ValueError("Company not found")

    total_size = 0

    # Function to calculate the size of data for a given model
    def get_table_data_size(model_class, company_id):
        total_size = 0
        rows = model_class.query.filter_by(company_id=company_id).all()

        # Text columns
        text_columns = [column.name for column in model_class.__table__.columns if isinstance(column.type, db.String)]
        for row in rows:
            for column in text_columns:
                value = getattr(row, column)
                if isinstance(value, str):  # Ensure the value is a string
                    total_size += len(value.encode('utf-8'))  # Size in bytes

        # Integer columns
        int_columns = [column.name for column in model_class.__table__.columns if isinstance(column.type, db.Integer)]
        for row in rows:
            for column in int_columns:
                value = getattr(row, column)
                if value is not None:
                    total_size += 4  # Size of an integer in bytes

        # Float/Decimal columns
        float_columns = [column.name for column in model_class.__table__.columns if isinstance(column.type, (db.Float, db.Numeric))]
        for row in rows:
            for column in float_columns:
                value = getattr(row, column)
                if value is not None:
                    total_size += 8  # Size of a double-precision float in bytes

        # Date/Time columns
        datetime_columns = [column.name for column in model_class.__table__.columns if isinstance(column.type, db.DateTime)]
        for row in rows:
            for column in datetime_columns:
                value = getattr(row, column)
                if value is not None:
                    total_size += 8  # Size of a datetime in bytes

        # Boolean columns
        boolean_columns = [column.name for column in model_class.__table__.columns if isinstance(column.type, db.Boolean)]
        for row in rows:
            for column in boolean_columns:
                value = getattr(row, column)
                if value is not None:
                    total_size += 1  # Size of a boolean in bytes

        return total_size

    # Calculate the size for Company model data
    def get_company_size(company):
        total_size = 0

        # Text columns
        text_columns = [
            'title', 'description', 'logo_url', 'location', 'category', 'nature',
            'email', 'phone_number', 'website_url', 'linkedin_url', 'twitter_url',
            'facebook_url', 'number_of_employees', 'annual_revenue', 'currency', 'tags'
        ]
        for column in text_columns:
            value = getattr(company, column)
            if isinstance(value, str):  # Ensure the value is a string
                total_size += len(value.encode('utf-8'))

        # Integer columns
        int_columns = ['id', 'year_established']
        for column in int_columns:
            value = getattr(company, column)
            if value is not None:
                total_size += 4  # Size of an integer in bytes

        # Float/Decimal columns (if applicable)
        float_columns = []  # Add any float/decimal columns here
        for column in float_columns:
            value = getattr(company, column)
            if value is not None:
                total_size += 8  # Size of a double-precision float in bytes

        # Date/Time columns
        datetime_columns = ['registration_date']
        for column in datetime_columns:
            value = getattr(company, column)
            if value is not None:
                total_size += 8  # Size of a datetime in bytes

        # Boolean columns
        boolean_columns = ['is_active']
        for column in boolean_columns:
            value = getattr(company, column)
            if value is not None:
                total_size += 1  # Size of a boolean in bytes

        return total_size

    # Add company-specific data size
    total_size += get_company_size(company)

    # Include the data size from related tables
    related_tables = [
        User, Section, Article, AudioBook, Invoice,
        Subject, Class, Finance, Student, Book, AudioBook,
        Session, Teacher, Exam, Expense, Folder, Job, Note,
        MarketingCampaign, Employee, Project
    ]

    for table in related_tables:
        total_size += get_table_data_size(table, company_id)

    return total_size





def get_employee_stats(company_id):
    """Calculate employee-related statistics"""
    total_employees = db.session.query(db.func.count(Employee.id)).filter(
        Employee.company_id == company_id
    ).scalar() or 0
    
    # Calculate percentage change from last month
    last_month = datetime.utcnow() - timedelta(days=30)
    prev_month_count = db.session.query(db.func.count(Employee.id)).filter(
        Employee.company_id == company_id,
        Employee.member_since < last_month
    ).scalar() or 0
    
    percentage_change = 0
    if prev_month_count > 0:
        percentage_change = ((total_employees - prev_month_count) / prev_month_count) * 100
    
    return {
        'total_employees': total_employees,
        'percentage_change': round(percentage_change, 1)
    }


def get_expense_stats(company_id):
    """Calculate expense-related statistics using CompanyExpense"""
    # Calculate total expenses using the total_cost hybrid property
    total_expenses = db.session.query(
        db.func.sum(CompanyExpense.unit_price * CompanyExpense.quantity)
    ).filter(
        CompanyExpense.invoice.has(company_id=company_id),
        CompanyExpense.is_gain == False  # Only count actual expenses, not gains
    ).scalar() or 0
    
    # Calculate percentage change from last month
    last_month = datetime.utcnow() - timedelta(days=30)
    prev_month_expenses = db.session.query(
        db.func.sum(CompanyExpense.unit_price * CompanyExpense.quantity)
    ).filter(
        CompanyExpense.invoice.has(company_id=company_id),
        CompanyExpense.is_gain == False,
        CompanyExpense.date >= last_month - timedelta(days=30),
        CompanyExpense.date < last_month
    ).scalar() or 0
    
    percentage_change = 0
    if prev_month_expenses > 0:
        percentage_change = ((total_expenses - prev_month_expenses) / prev_month_expenses) * 100
    
    return {
        'total_expenses': total_expenses,
        'percentage_change': round(percentage_change, 1)
    }

def get_project_stats(company_id):
    """Calculate project-related statistics"""
    # Number of projects
    total_projects = db.session.query(db.func.count(Folder.id)).filter(
        Folder.company_id == company_id
    ).scalar() or 0
    
    # Max budget
    max_budget = db.session.query(db.func.max(Folder.budget)).filter(
        Folder.company_id == company_id
    ).scalar() or 0
    
    return {
        'total_projects': total_projects,
        'max_budget': max_budget
    }