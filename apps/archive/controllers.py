from flask import request, render_template, jsonify, redirect, url_for, flash, abort, make_response, current_app
from datetime import datetime
from flask_login import login_required, current_user
from . import archive
from ..models.general.folder import Folder
from ..models.general.file import File
from ..models.general.company import Company
from ..models.school.book import Book
from ..models.general.audiobook import AudioBook
from ..models.school.book_loan import BookLoan
from ..models.general.user import User
from ..models.general.role import Role
from ..decorators import librarian_required
from ..utils import save_files
from ..auth.utils import save_file_locally, check_internet_connection, get_resource_path
from .. import db
from math import ceil
from flask_babel import gettext as _
from dotenv import load_dotenv
import os
from .emails.notify_folder import notify_for_new_folder, notify_for_deleted_folder, notify_users_about_new_files
from firebase_admin import storage
from ..user.support_team.business.insights import get_relevant_urls_for_company, get_data_size_for_company
from ..models.general.user import User, generate_password_hash
import weasyprint

load_dotenv()

@archive.route("/folders/<int:company_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def folders(company_id):
    company = Company.query.get_or_404(company_id)
    category = company.category

    if request.method == 'GET':

        page = request.args.get('page', 1, type=int)
        folders = Folder.query.filter_by(company_id=company.id).all()

        return render_template(
            f"dashboard/@support_team/{category.lower()}/folders.html",
            folders=folders, 
            company=company,
            page=page
        )

    if request.method == 'POST':
        data = request.json
        new_folder = Folder(
            name=data['folder_name'],
            budget=float(data.get('budget', 0.0)),
            currency=data.get('currency', ''),
            deadline=datetime.fromisoformat(data['deadline']),
            company_id=company.id
        )


        if category == 'Shipping':
            new_folder.transport = data.get('transport', '')
            new_folder.weight = data.get('weight', '')
            new_folder.bills_of_ladding = data.get('bills_of_ladding', '')

        elif category == 'Engineering':
            new_folder.project_location = data.get('project_location', '')
            new_folder.project_manager = data.get('project_manager', '')
            new_folder.project_phase = data.get('project_phase', '')
            new_folder.budget = data.get('budget', 0.0)
            new_folder.contractor = data.get('contractor', '')
            new_folder.materials_used = data.get('materials_used', '')
            new_folder.permits_approved = data.get('permits_approved', False)
            new_folder.species_studied = data.get('species_studied', '')
            new_folder.experiment_date = datetime.fromisoformat(data.get('experiment_date', datetime.utcnow().isoformat()))
            new_folder.lab_technician = data.get('lab_technician', '')
            new_folder.sample_storage = data.get('sample_storage', '')
            new_folder.biosafety_level = data.get('biosafety_level', 1)
            new_folder.voltage = data.get('voltage', 0.0)
            new_folder.current = data.get('current', 0.0)
            new_folder.circuit_diagram = data.get('circuit_diagram', '')
            new_folder.compliance_standards = data.get('compliance_standards', '')
            new_folder.pipe_material = data.get('pipe_material', '')
            new_folder.water_pressure = data.get('water_pressure', 0.0)
            new_folder.plumbing_diagram = data.get('plumbing_diagram', '')
            new_folder.pcb_layout = data.get('pcb_layout', '')
            new_folder.components_list = data.get('components_list', '')
            new_folder.firmware_version = data.get('firmware_version', '')

            

        db.session.add(new_folder)
        db.session.commit()


        if check_internet_connection():
            notify_for_new_folder(
                company_name=company.title,
                folder_name=new_folder.name,
                deadline=new_folder.deadline,
                company_id=company.id
            )
            

        return jsonify({
            'title': _('Nouveau dossier ajouté'),
            'success': True,
            'message': _(f"Le dossier N°{new_folder.id} vient d\'être crée"),
            'confirmButtonText': _('OK'),
        }), 201

    if request.method == 'DELETE':
        data = request.get_json()
        folder_id = data.get('id')
        
        if not folder_id:
            return jsonify({
                'title': _('Erreur'),
                'error': _('ID du dossier manquant'),
                'confirmButtonText': _('OK')
            }), 400

        folder = Folder.query.get(folder_id)
        
        if not folder:
            return jsonify({
                'title': _('Dossier introuvable'),
                'error': _('Dossier introuvable'),
                'confirmButtonText': _('OK')
            }), 404

        try:
            files = File.query.filter_by(folder_id=folder_id).all()
            for file in files:
                try:
                    if check_internet_connection() and not file.filepath.startswith('/local_files/'):
                        pass
                    
                    elif file.filepath.startswith('/local_files/'):
                        file_path = os.path.join(
                            get_resource_path('client_folder'),
                            os.path.basename(file.filepath)
                        )
                        if os.path.exists(file_path):
                            os.remove(file_path)
                except Exception as file_error:
                    current_app.logger.error(f"Error deleting file {file.id}: {file_error}")
                
                db.session.delete(file)
            
            company = Company.query.get(folder.company_id)
            db.session.delete(folder)
            db.session.commit()

            if check_internet_connection():
                notify_for_deleted_folder(
                    company_name=company.title,
                    folder_name=folder.name,
                    folder_id=folder_id,
                    company_id=folder.company_id
                )

            return jsonify({
                'title': _('Supprimé'),
                'message': _("Le dossier et son contenu ont été supprimés avec succès"),
                'confirmButtonText': _('OK')
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Folder deletion error: {str(e)}")
            return jsonify({
                'title': _('Erreur'),
                'error': _('Échec de la suppression du dossier'),
                'details': str(e),
                'confirmButtonText': _('OK')
            }), 500
    
        
@archive.route('/search_folders_files/<int:company_id>', methods=['GET'])
@login_required
def search_folders_files(company_id):

    placeholder_url = current_app.config.get('PLACEHOLDER_STATIC_URL')

    company = Company.query.get_or_404(company_id)
    query = request.args.get('query', '')
    
    folders = Folder.query.filter(
        Folder.name.ilike(f'%{query}%'),
        Folder.company_id == company.id
    ).all()
    
    files = File.query.join(Folder).filter(
        File.label.ilike(f'%{query}%'),
        Folder.company_id == company.id
    ).all()
    
    results = []
    
    for folder in folders:
        results.append({
            'label': folder.name,
            'type': 'Folder',
            'icon': '<i class="bi bi-folder"></i>'
        })
    
    results = []

    for file in files:
        ext = file.filepath.split('.')[-1].lower()
        icon = ''
        if ext in ['pdf']:
            icon = f'<img src="{placeholder_url}pdf.png" alt="{file.label}" class="img-thumbnail me-2 custom-thumbnail" style="width: 50px;">'
        elif ext in ['jpg', 'jpeg', 'png']:
            icon = f'<img src="{placeholder_url}image.png" alt="{file.label}" class="img-thumbnail me-2 custom-thumbnail" style="width: 50px;">'
        else:
            icon = '<i class="bi bi-file-earmark"></i>'

        results.append({
            'label': file.label,
            'uploaded_at': file.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'url': file.filepath,
            'type': ext.upper(),
            'icon': icon,
            'folder_name': file.folder.name
        })


    return jsonify({'results': results})



@archive.route('/folders/<int:folder_id>/close/<int:company_id>', methods=['PUT'])
@login_required
def close_folder(folder_id, company_id):
    try:
        folder = Folder.query.get_or_404(folder_id)
        company = Company.query.get_or_404(company_id)
        folder.status = True 
        db.session.commit()

        """
        warn people when a folder
        status has been changed
        send a notification when 
        a folder is changed
        """

        return jsonify(
            {
                'title': _(f"Dossier N°{folder_id} fermé"),
                'message': _(f"Le dossier N°{folder_id} vient d\'être fermé"),
                'confirmButtonText': _('OK')
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to close folder: {str(e)}'}), 500


@archive.route('/save_folder_files/<int:folder_id>/<int:company_id>', methods=['POST'])
@login_required
def save_folder_files(folder_id, company_id):
    company = Company.query.get_or_404(company_id)
    folder = Folder.query.get_or_404(folder_id)
    folder_title = folder.name

    files = request.files.getlist('files[]')
    labels = request.form.getlist('labels[]')

    if len(files) != len(labels):
        return jsonify({
            'title': _('Erreur'),
            'error': _('Le nombre de labels et les fichiers ne correspondent pas'),
            'confirmButtonText': _('OK')
        }), 400

    has_internet = check_internet_connection()
    
    saved_files = []
    for file in files:
        if has_internet:
            try:
                saved_file = save_files([file], "client_folder")[0]
                saved_files.append(saved_file)
            except Exception as e:
                save_result = save_file_locally(file, "client_folder")
                saved_files.append(url_for('auth.local_files',
                    folder='client_folder',
                    filename=os.path.basename(save_result["absolute_path"]),
                    _external=True))
        else:
            save_result = save_file_locally(file, "client_folder")
            saved_files.append(url_for('auth.local_files',
                folder='client_folder',
                filename=os.path.basename(save_result["absolute_path"]),
                _external=True))

    for i, file_url in enumerate(saved_files):
        new_file = File(
            label=labels[i],
            filepath=file_url,
            folder_id=folder.id
        )
        db.session.add(new_file)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'title': _('Erreur'),
            'error': _('Une erreur est survenue lors de la sauvegarde des fichiers'),
            'confirmButtonText': _('OK')
        }), 500

    if has_internet:
        notify_users_about_new_files(
            company=company, 
            folder=folder, 
            files=files, 
            labels=labels
        )

    return jsonify({
        'title': _('Fichiers sauvegardés'),
        'message': _(f"Le(s) fichier(s) ont été sauvegardé(s) dans {folder_title}"), 
        'files': saved_files,
        'confirmButtonText': _('OK'),
    })


@archive.route('/get_folders_list/<int:company_id>', methods=['GET'])
def get_folders(company_id):
    company = Company.query.get_or_404(company_id)
    folders = Folder.query.filter_by(company_id=company.id).all()
    folder_list = [{
        'id': folder.id,
        'description': folder.description,
        'client': folder.client,
        'bills_of_ladding': folder.bills_of_ladding,
    } for folder in folders]
    return jsonify(folder_list)


@archive.route('/manage_books/<int:company_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@librarian_required
def manage_books(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        per_page = 10
        sort_by = request.args.get('sort', 'title')  # Default sorting by title
        offset = (page - 1) * per_page

        books_query = Book.query.filter_by(company_id=company_id)
        
        if sort_by == 'title':
            books_query = books_query.order_by(Book.title)
        elif sort_by == 'newest':
            books_query = books_query.order_by(Book.published_date.desc()) 
        elif sort_by == 'author':
            books_query = books_query.order_by(Book.author)
        
        total_books = books_query.count()
        books = books_query.offset(offset).limit(per_page).all()
        
        total_pages = ceil(total_books / per_page)

        users = User.query.filter(
            User.company_id == company_id,
            User.role.has(Role.name != 'Librarian')
        ).all()


        return render_template(
            'dashboard/@support_team/school/manage_books.html',
            books=books,
            company=company,
            page=page,
            total_pages=total_pages,
            sort_by=sort_by,
            users=users
        )

    elif request.method == 'POST':
        # Adding a new book
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        image_file = request.files.get('image')
        ebook_file = request.files.get('ebook')

        if title and author and category:
            image_url = None
            ebook_url = None

            if image_file:
                image_url = save_files([image_file], 'book_pictures')

            if ebook_file:
                ebook_url = save_files([ebook_file], 'ebook_files')

            new_book = Book(
                title=title,
                author=author,
                category=category,
                image_url=image_url[0] if image_url else None,
                ebook_url=ebook_url[0] if ebook_file else None,
                company_id=company_id
            )
            db.session.add(new_book)
            db.session.commit()
            
            """
            Warn students and user when new books are added
            in their libraries, we will check their interests
            using using their own preferences and other more hidden 
            data
            """
            return jsonify(
                {
                    'title': _('Nouveau livre ajouté'),
                    'success': True, 
                    'message': _(f"Le livre {new_book.title} a bien été ajouté"),
                    'confirmButtonText': _('OK') 
                }
            ), 201
        else:
            return jsonify(
                {
                    'title': _('Infos incomplètes'),
                    "success": False, 
                    "message": _('Tous les champs sont requis'),
                    'confirmButtonText': _('OK')
                }
            ), 400

    elif request.method == 'PUT':
        data = request.json
        book_id = data.get('id')
        book = Book.query.filter_by(id=book_id, company_id=company_id).first()

        if not book:
            return jsonify(
                {
                    'title': _('Livre introuvable'),
                    'success': False, 
                    'message': _('Livre introuvable'),
                    'confirmButtonText': _('OK')
                }
            ), 404

        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.category = data.get('category', book.category)

        db.session.commit()
        return jsonify(
            {
                'title': _('Infos mises à jour'),
                "success": True, 
                "message": _('Infos mises à jour'),
                'confirmButtonText': _('OK')
            }
        ), 200

    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        book_id = data.get('Id')
        book = Book.query.filter_by(id=book_id, company_id=company_id).first()

        if not book:
            return jsonify(
                {
                    'title': _('Livre introuvable'),
                    'success': False, 
                    'message': _('Livre introuvable'),
                    'confirmButtonText': _('OK')
                }
            ), 404

        db.session.delete(book)
        db.session.commit()
        return jsonify(
            {
                'title': _('Supprimé'),
                "success": True, 
                "message": _('Livre supprimé')
            }
        ), 200

    return jsonify(
        {
            'title': _('Erreur'),
            "success": False, 
            "message": _('Requête invalide')
        }
    ), 405

@archive.route('/manage_audiobooks/<int:company_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@librarian_required
def manage_audiobooks(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        per_page = 10
        sort_by = request.args.get('sort', 'title')  # Default sorting by title
        offset = (page - 1) * per_page

        audiobooks_query = AudioBook.query.filter_by(company_id=company_id)
        
        if sort_by == 'title':
            audiobooks_query = audiobooks_query.order_by(AudioBook.title)
        elif sort_by == 'newest':
            audiobooks_query = audiobooks_query.order_by(AudioBook.release_date.desc())
        elif sort_by == 'author':
            audiobooks_query = audiobooks_query.order_by(AudioBook.author)
        
        total_audiobooks = audiobooks_query.count()
        audiobooks = audiobooks_query.offset(offset).limit(per_page).all()
        
        total_pages = ceil(total_audiobooks / per_page)

        return render_template(
            'dashboard/@support_team/audiobooks.html',
            audiobooks=audiobooks,
            company=company,
            page=page,
            total_pages=total_pages,
            sort_by=sort_by
        )

    elif request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        narrator = request.form.get('narrator')
        duration = request.form.get('duration')
        release_date = request.form.get('release_date')
        category = request.form.get('category')
        audio_file = request.files.get('audio')
        image_file = request.files.get('image')

        if title and author and category:
            image_url = None
            audio_url = None

            if audio_file:
                audio_url = save_files([audio_file], 'audiobooks')

            if image_file:
                image_url = save_files([image_file], 'book_pictures')

            new_audiobook = AudioBook(
                title=title,
                author=author,
                narrator=narrator,
                duration=duration,
                release_date=release_date,
                category=category,
                image_url=image_url[0] if image_url else None,
                audio_url=audio_url[0] if audio_file else None,
                company_id=company_id
            )
            db.session.add(new_audiobook)
            db.session.commit()

            """
            Warn interested users while the books are 
            available
            """

            return jsonify(
                {
                    'title': _('Livre audio ajouté'),
                    'success': True,
                    'message': _(f"Le livre {new_audiobook.title} de {new_audiobook.author} vient d\'être ajouté"),
                    'confirmButtonText': _('OK')
                }
            ), 201
        else:
            return jsonify(
                {
                    'title': _('Infos incompletes!'),
                    "success": False, 
                    "message": _("Tous les champs sont requis"),
                    'confirmButtonText': _('OK')
                }
            ), 400

    elif request.method == 'PUT':
        data = request.json
        audiobook_id = data.get('id')
        audiobook = AudioBook.query.filter_by(id=audiobook_id, company_id=company_id).first()

        if not audiobook:
            return jsonify(
                {
                    'title': _('Livre introuvable'),
                    'success': False,
                    'message': _('Livre audio introuvable'),
                    'confirmButtonText': _('OK')
                }
            ), 404

        audiobook.title = data.get('title', audiobook.title)
        audiobook.author = data.get('author', audiobook.author)
        audiobook.narrator = data.get('narrator', audiobook.narrator)
        audiobook.duration = data.get('duration', audiobook.duration)
        audiobook.release_date = data.get('release_date', audiobook.release_date)
        audiobook.category = data.get('category', audiobook.category)

        # Handle file uploads
        audio_file = request.files.get('audio')
        image_file = request.files.get('image')
        if audio_file:
            audio_url = save_files([audio_file], 'audiobook_files')
            audiobook.audio_url = audio_url[0] if audio_file else audiobook.audio_url
        if image_file:
            image_url = save_files([image_file], 'image_files')
            audiobook.image_url = image_url[0] if image_file else audiobook.image_url

        db.session.commit()
        return jsonify(
            {
                'title': _('Mise à jour effectué'),
                'success': True, 
                'message': _('Livre audio mis à jour'),
                'confirmButtonText': _('OK')
            }
        ), 200

    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        audiobook_id = data.get('id')
        audiobook = AudioBook.query.filter_by(id=audiobook_id, company_id=company_id).first()

        if not audiobook:
            return jsonify(
                {
                    'success': False, 
                    'message': _('Livre audio introuvable'),
                    'title': _('Livre introuvable')
                }
            ), 404

        db.session.delete(audiobook)
        db.session.commit()
        return jsonify(
            {
                'title': _('Supprimé'),
                'success': True, 
                'message': _('Livre audio supprimé')
            }
        ), 200

    return jsonify(
        {
            "success": False, 
            "message": "Invalid request"
        }
    ), 405



@archive.route('/search_books')
@login_required
@librarian_required
def search_books():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    search_query = f"%{query}%"
    results = db.session.query(Book).filter(
        Book.title.ilike(search_query) |
        Book.author.ilike(search_query) |
        Book.category.ilike(search_query)
    ).all()

    results_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'category': book.category,
        'image_url': book.image_url
    } for book in results]

    return jsonify(results_list)

@archive.route('/search_audio_books')
@login_required
@librarian_required
def search_audio_books():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    search_query = f"%{query}%"
    results = db.session.query(Audiobook).filter(
        Audiobook.title.ilike(search_query) |
        Audiobook.author.ilike(search_query) |
        Audiobook.category.ilike(search_query)
    ).all()

    results_list = [{
        'id': audiobook.id,
        'title': audiobook.title,
        'author': audiobook.author,
        'category': audiobook.category,
        'image_url': audiobook.image_url
    } for audiobook in results]

    return jsonify(results_list)


@archive.route('/lend_book/<int:company_id>/<int:book_id>', methods=['POST'])
@login_required
@librarian_required
def lend_book(company_id, book_id):
    company = Company.query.get_or_404(company_id)
    borrower_id = request.form.get('borrower_name')
    return_date_str = request.form.get('return_date')
    
    if not borrower_id or not return_date_str:
        return jsonify({'success': False, 'message': 'Nom et date de retour requis'}), 400
    
    try:
        return_date = datetime.strptime(return_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify(
            {
                'title': _('Format de la date invalide!'),
                'success': False, 
                'message': _('Format de la date invalide')
            }
        ), 400

    new_loan = BookLoan(
        user_id=borrower_id,
        book_id=book_id,
        loan_date=datetime.utcnow(),
        return_date=return_date,
        returned=False,
        company_id=company.id
    )
    
    db.session.add(new_loan)
    db.session.commit()

    return jsonify(
        {
            'title': _('Emprunt effectué'),
            'success': True, 
            'message': _('Emprunt effectué!')
        }
    ), 200

@archive.route('/manage_lendings/<int:company_id>')
@login_required
@librarian_required
def manage_lendings(company_id):
    company = Company.query.get_or_404(company_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    loans_query = BookLoan.query.filter_by(company_id=company_id, returned=False)

    pagination = loans_query.paginate(page=page, per_page=per_page, error_out=False)
    loans = pagination.items

    return render_template(
        'dashboard/@support_team/school/manage_book_lendings.html',
        company=company,
        loans=loans,
        pagination=pagination
    )

@archive.route('/mark_as_returned/<int:loan_id>/<int:company_id>', methods=['POST'])
@login_required
@librarian_required
def mark_as_returned(loan_id, company_id):
    try:
        loan = BookLoan.query.get(loan_id)

        if not loan:
            flash(_('Prêt introuvable.'), 'error')
            return redirect(url_for('archive.manage_loans'))

        loan.return_date = datetime.utcnow()
        loan.returned = True 
        db.session.commit()

        flash(_('Prêt marqué comme retourné avec succès.'), 'success')
        return redirect(url_for('archive.manage_loans', company_id=company_id))
    
    except Exception as e:
        flash( _(f'Une erreur est survenue: {str(e)}'), 'error')
        return redirect(url_for('archive.manage_loans', company_id=company_id))

@archive.route('/send-reminder/<int:loan_id>')
@login_required
@librarian_required
def send_reminder(loan_id):

    """
    implement automatic sytem
    for remind people to bring back
    the book
    """
    pass


@archive.route('/switch_lender/<int:loan_id>/<int:company_id>', methods=['POST'])
@login_required
@librarian_required
def switch_lender(loan_id, company_id):
    try:
        company = Company.query.get_or_404(company_id)
        new_lender_id = request.form.get('new_lender')
        return_date_str = request.form.get('return_date')
        loan = BookLoan.query.get(loan_id)

        if not loan:
            flash( _('Prêt introuvable.'), 'error')
            return redirect(url_for('archive.manage_lendings', company_id=company.id))

        loan.user_id = new_lender_id
        
        if return_date_str:
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d')
            loan.return_date = return_date
        
        db.session.commit()

        flash( _('Emprunteur changé avec succès.'), 'success')
        return redirect(url_for('archive.manage_lendings', company_id=company.id))
    except Exception as e:
        flash( _(f'Une erreur est survenue: {str(e)}'), 'error')
        return redirect(url_for('archive.manage_lendings', company_id=company.id))
    
@archive.route("/company_disk_usage/<int:company_id>", methods=['GET', 'POST'])
@login_required
def company_disk_usage(company_id):
    company = Company.query.get_or_404(company_id)
    if not current_user.is_ressync_sales_director():
        abort(403)

    bucket = storage.bucket()
    blobs = list(bucket.list_blobs())  # Convert the iterator to a list immediately

    companies = Company.query.all()
    company_disk_usages = []

    for company in companies:
        total_size = 0

        relevant_urls = get_relevant_urls_for_company(company.id)

        # Process each blob
        for blob in blobs:
            blob_url = f"https://storage.googleapis.com/afrilog-797e8.appspot.com/{blob.name}"

            # If the blob's URL is in the relevant URLs for this company, add its size
            if blob_url in relevant_urls:
                total_size += blob.size

        # Add text data size
        data_size = get_data_size_for_company(company.id)
        print(data_size)
        total_size += data_size

        # Store the company name and its total disk usage in MB
        company_disk_usages.append({
            'company_id': company.id,
            'company_name': company.title,
            'total_size_mb': total_size / (1024 * 1024)  # Convert to MB
        })

    # Sort by disk usage (optional)
    company_disk_usages.sort(key=lambda x: x['total_size_mb'], reverse=True)

    selected_company_id = request.args.get('company_id', default=None, type=int)

    # Filter the disk usage data based on the selected company
    if selected_company_id:
        company_disk_usages = [data for data in company_disk_usages if data['company_id'] == selected_company_id]

    return render_template(
        "dashboard/@support_team/company_disk_usage.html", 
        company_disk_usages=company_disk_usages,
        companies=companies,
        company=company
    )


# these apis are for archiving system for solo entrepreneurs

@archive.route('/get-my-client-folders/<int:user_id>', methods=['GET', 'POST'])
def handle_user_client_folders(user_id):
    user = User.query.get(user_id)
    
    if not user:
        if User.query.count() == 0:
            user = User(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=generate_password_hash("admin123", method='sha256'),
                username="admin",
                gender="Not specified",
                address="Headquarters",
                member_since=datetime.utcnow(),
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id

    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        folders = Folder.query.filter_by(user_id=user_id).paginate(page=page, per_page=limit, error_out=False)
        folder_data = [
            {
                "id": folder.id,
                "name": folder.name,
                "client": folder.client,
                "created_at": folder.created_at.strftime('%Y-%m-%d'),
                "unique_id": folder.unique_id,
                "number": folder.folder_number,
            }
            for folder in folders.items
        ]
        
        return jsonify({
            "folders": folder_data,
            "total": folders.total,
            "pages": folders.pages,
            "current_page": folders.page,
        })

    elif request.method == 'POST':
        data = request.json
        name = data.get('name', '').strip()
        client = data.get('client', '').strip()
        company_id = data.get('company_id', '')
        description = data.get('comments', '').strip()
        archive_date = data.get('date')

        if not name:
            return jsonify({"error": "Le nom du dossier est requis", "field": "folderName"}), 400

        if not client:
            return jsonify({"error": "Nom du client est requis", "field": "folderClient"}), 400

        try:
            if archive_date:
                archive_date = datetime.strptime(archive_date, '%Y-%m-%d')
            else:
                archive_date = datetime.utcnow()

            new_folder = Folder(
                name=name,
                client=client,
                user_id=user_id,
                company_id=company_id,
                description=description,
                created_at=archive_date
            )

            db.session.add(new_folder)
            db.session.commit()

            return jsonify({
                "message": "Folder created successfully",
                "folder": {
                    "id": new_folder.id,
                    "name": new_folder.name,
                    "client": new_folder.client,
                    "description": new_folder.description,
                    "created_at": new_folder.created_at.strftime('%Y-%m-%d')
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@archive.route('/get-folder-details/<int:folder_id>', methods=['GET'])
def get_folder_details(folder_id):
    try:
        folder = Folder.query.get(folder_id)
        if folder is None:
            return jsonify({"error": "Folder not found"}), 404
        
        files = File.query.filter_by(folder_id=folder.id).all()
        file_details = []
        
        for file in files:
            file_details.append({
                "name": file.label,
                "file_type": file.filepath.split('.')[-1] if file.filepath else "unknown",
                "url": file.filepath or None 
            })
        
        folder_details = {
            "id": folder.id,
            "name": folder.name,
            "client": folder.client,
            "description": folder.description,
            "created_at": folder.created_at.strftime('%Y-%m-%d'),
            "unique_id": folder.unique_id,
            "number": folder.folder_number,
            "files": file_details
        }

        return jsonify(folder_details)
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@archive.route('/edit-my-client-folder/<int:folder_id>', methods=['PUT'])
def edit_folder(folder_id):
    data = request.get_json()

    folder = Folder.query.get(folder_id)

    if folder is None:
        return jsonify({"error": "Folder not found"}), 404

    new_name = data.get('name')
    new_client = data.get('client')

    if not new_name:
        return jsonify({"error": "Folder name is required"}), 400

    folder.name = new_name
    folder.client = new_client

    try:
        db.session.commit()
        return jsonify({"message": "Folder updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating folder: {str(e)}"}), 500


@archive.route('/attach-my-client-files/<int:folder_id>', methods=['POST'])
def attach_my_client_files(folder_id):
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({"error": "Folder not found"}), 404

    folder_path = os.path.join(os.environ.get('ARCHIVE_STATIC_DIR'), folder.name)
    os.makedirs(folder_path, exist_ok=True)

    try:
        files = request.files.getlist('files[]')
        labels = request.form.getlist('labels[]')

        if len(labels) == 0:
            return jsonify({"error": "At least one label is required."}), 400

        saved_entries = []

        for i, label in enumerate(labels):
            file = files[i] if i < len(files) else None

            if label and not file:
                new_entry = File(
                    label=label,
                    filepath=None,
                    folder_id=folder.id,
                    uploaded_at=datetime.utcnow(),
                    user_id=1,
                    company_id=1
                )
                db.session.add(new_entry)
                saved_entries.append({"label": label, "url": None})

            elif label and file:
                file_path = os.path.join(folder_path, file.filename)
                file.save(file_path)

                file_url = url_for('static', filename=os.path.join('uploads', folder.name, file.filename), _external=True)

                new_entry = File(
                    label=label,
                    filepath=file_url,
                    folder_id=folder.id,
                    uploaded_at=datetime.utcnow(),
                    user_id=1,
                    company_id=1
                )
                db.session.add(new_entry)
                saved_entries.append({"label": label, "url": file_url})

        db.session.commit()

        return jsonify({
            "message": "Labels and files successfully attached.",
            "saved_entries": saved_entries
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@archive.route('/delete-folder/<int:folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({"error": "Folder not found"}), 404

    try:
        folder_path = os.path.join(os.environ.get('ARCHIVE_STATIC_DIR'), folder.name)
        if os.path.exists(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(folder_path)

        File.query.filter_by(folder_id=folder.id).delete()

        db.session.delete(folder)
        db.session.commit()

        return jsonify({"message": "Folder and its contents have been deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred while deleting the folder: {str(e)}"}), 500
    

@archive.route('/get-files-by-user/<int:user_id>', methods=['GET'])
def get_files_by_user(user_id):
    files = File.query.filter_by(user_id=user_id).all()
    
    if not files:
        return jsonify([])

    files_data = []
    
    for file in files:
        folder = Folder.query.get(file.folder_id)
        

        file_data = {
            "id": file.id,
            "label": file.label,
            "filepath": file.filepath,
            "uploaded_at": file.uploaded_at,
            "folder_name": folder.name,
            "folder_id": folder.unique_id,
            "client_name": folder.client
        }
        files_data.append(file_data)

    return jsonify(files_data)

@archive.route('/delete-file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    file = File.query.get(file_id)
    if not file:
        return jsonify({"error": "File not found"}), 404

    try:
        if file.filepath:
            file_path = os.path.join(os.environ.get('ARCHIVE_STATIC_DIR', ''), file.filepath)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(file)
        db.session.commit()

        return jsonify({"message": "fichier correctement supprimé"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@archive.route('/search-user-folders-or-files/<int:user_id>', methods=['GET'])
def search_user_folders_or_files(user_id):
    query = request.args.get('query', '').strip()

    folders = Folder.query.filter(
        (Folder.name.ilike(f'%{query}%')) | 
        (Folder.unique_id.ilike(f'%{query}%')),
        Folder.user_id == user_id
    ).all()

    results = []
    for folder in folders:
        files = File.query.filter(File.folder_id == folder.id).all()
        
        folder_data = {
            'id': folder.id,
            'name': folder.name,
            'unique_id': folder.unique_id,
            'client_name': folder.client,
            'files': [{
                'id': file.id,
                'label': file.label,
                'filepath': file.filepath,
                'uploaded_at': file.uploaded_at
            } for file in files]
        }
        results.append(folder_data)

    return jsonify(results)


@archive.route('/generate-pdf-folders-list/<int:user_id>', methods=['GET'])
def generate_pdf(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    folders = Folder.query.filter_by(user_id=user_id).all()
    
    folder_data = [
        {
            "id": folder.id,
            "name": folder.name,
            "client": folder.client,
            "created_at": folder.created_at.strftime('%Y-%m-%d'),
            "unique_id": folder.unique_id,
            "number": folder.folder_number
        }
        for folder in folders
    ]
    
    html = render_template('reports/solopreneur/archives_report.html', folders=folder_data)
    
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=folders_report.pdf'
    
    return response