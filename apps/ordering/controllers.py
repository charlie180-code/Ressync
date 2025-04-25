from flask import render_template, jsonify, request, abort, flash, redirect, url_for, send_file, make_response
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from ..models.shipping.purchase import Purchase
from ..models.shipping.authorization import Authorization
from ..models.general.company import Company
from ..utils import save_files, generate_qr_code
import secrets
from ..utils import save_product_pictures, save_docs, generate_barcode
from datetime import datetime
from .. import db
from . import order
import os
from ..decorators import customer_required, agent_required
from flask_babel import gettext as _
from weasyprint import HTML
from datetime import datetime
from sqlalchemy import or_, and_
import json
import io

@order.route("/my_purchases/previous_purchase_requests/<int:company_id>")
@login_required
@customer_required
def previous_purchase_requests(company_id):
    company = Company.query.get_or_404(company_id)
    purchases = Purchase.query.filter_by(user_id=current_user.id, company_id=company.id).all()
    return render_template("dashboard/customers/previous_purchase_requests.html", purchases=purchases, company=company)

@order.route("/purchases/<int:id>/<int:company_id>", methods=['GET'])
@login_required
@customer_required
def get_purchase_details(id, company_id):
    purchase = Purchase.query.get_or_404(id, company_id)
    if purchase.user_id != current_user.id:
        abort(403)
    return jsonify({
        'title': purchase.title,
        'token': purchase.token,
        'status': purchase.status,
        'start_check': purchase.start_check,
        'description': purchase.description,
        'author_first_name': purchase.author_first_name,
        'author_last_name': purchase.author_last_name,
        'author_email_address': purchase.author_email_address,
        'author_phone_number': purchase.author_phone_number,
        'author_address': purchase.author_address,
        'author_country': purchase.location,
        'qr_code_url': purchase.qr_code_url
    })


@order.route("/quotes/previouses/<int:company_id>")
@login_required
@customer_required
def previous_quotes(company_id):
    company = Company.query.get_or_404(company_id)
    user_id = current_user.id
    user_requests = Authorization.query.filter_by(user_id=user_id, company_id=company.id).all()
    return render_template("dashboard/customers/previous_quotes.html", user_requests=user_requests, company=company)


@order.route("/new_previouses/<int:company_id>")
@login_required
@agent_required
def new_quotes(company_id):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    company = Company.query.get_or_404(company_id)
    pagination = Authorization.query.filter_by(company_id=company.id).paginate(page=page, per_page=per_page)
    return render_template(
        "dashboard/@support_team/quotes_list.html", 
        quotes=pagination.items, 
        pagination=pagination, 
        company=company
    )


@order.route("/new_purchases/<int:company_id>")
@login_required
def new_purchases(company_id):
    if not (current_user.is_responsible() or current_user.is_sales()):
        abort(403)
    company = Company.query.get_or_404(company_id)
    purchases = Purchase.query.filter_by(status=False, company_id=company.id).all()
    return render_template("dashboard/@support_team/new_purchases.html", purchases=purchases, company=company)



@order.route("/quotes/apply/<int:company_id>", methods=['GET', 'POST'])
@login_required
@customer_required
def apply_quotes(company_id):
    company =  Company.query.get_or_404(company_id)
    if request.method == 'POST':
        data = request.form
        files = request.files

        try:
            client_first_name = data.get('client_first_name')
            client_last_name = data.get('client_last_name')
            client_phone_number = data.get('client_phone_number')
            client_location = data.get('client_location')
            lading_number = data.get('lading_number')
            agent_first_name = data.get('agent_first_name')
            agent_last_name = data.get('agent_last_name')
            shipping_company_title = data.get('shipping_company_title')

            client_signature_file = files.get('client_signature_url')
            client_id_file = files.get('client_id_card_url')

            saved_files = save_files([client_signature_file, client_id_file], "authorization_files")
            client_signature_url = saved_files[0] if len(saved_files) > 0 else ''
            client_id_card_url = saved_files[1] if len(saved_files) > 1 else ''

            qr_code_path = generate_qr_code(lading_number)

            new_authorization = Authorization(
                client_first_name=client_first_name,
                client_last_name=client_last_name,
                client_phone_number=client_phone_number,
                client_location=client_location,
                lading_bills_identifier=lading_number,
                agent_first_name=agent_first_name,
                agent_last_name=agent_last_name,
                shipping_company_title=shipping_company_title,
                client_signature_url=client_signature_url,
                client_id_card_url=client_id_card_url,
                user_id=current_user.id,
                company_id=company.id
            )

            db.session.add(new_authorization)
            db.session.commit()

            return jsonify({'success': True, 'message': _('Votre requête a bien été envoyé')}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    return render_template('api/customers/authorizations/apply.html', company=company)


@order.route("/my_purchases/track_my_product/user/<int:company_id>", methods=['GET'])
def get_user_purchases(company_id):
    company = Company.query.get_or_404(company_id)
    user_id = current_user.id if current_user.is_authenticated else None
    purchases = Purchase.query.filter_by(user_id=user_id, company_id=company.id).all()
    return jsonify([{
        'token': purchase.token,
        'title': purchase.title
    } for purchase in purchases])


@order.route("/purchases/request/<int:company_id>", methods=['GET', 'POST'])
@login_required
@customer_required
def purchase_request(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        data = request.form
        files = request.files
        token = secrets.token_urlsafe(16)
        
        product_picture_paths = []
        if 'product_picture_url' in files:
            product_picture_paths = save_product_pictures(files.getlist('product_picture_url'))
        
        doc_paths = []
        if 'doc_url' in files:
            doc_paths = save_docs(files.getlist('doc_url'))
        
        barcode_url = generate_barcode(token)

        purchase = Purchase(
            title=data['title'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name'],
            author_address=data['author_address'],
            author_email_address=data['author_email_address'],
            product_length=float(data.get('product_length', 0.0)),
            product_width=float(data.get('product_width', 0.0)),
            author_phone_number=data['author_phone_number'],
            location=data['location'],
            provider=data.get('provider'),
            product_picture_url=product_picture_paths[0] if product_picture_paths else None,
            description=data['description'],
            category=data['category'],
            doc_url=doc_paths[0] if doc_paths else None,
            user_id=current_user.id,
            token=token,
            qr_code_url=generate_qr_code(token),
            barcode_url=barcode_url,
            start_check=datetime.utcnow(),
            company_id=company.id
        )

        db.session.add(purchase)

        try:
            db.session.commit()

            return jsonify({
                'title': _('Envoyé avec succès'), 
                'message': _('Votre requête a été bien envoyée'), 
                'token': token
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return render_template('api/customers/goods/purchase_request.html', company=company)


@order.route('/my_purchases/delete/<int:purchase_id>', methods=['DELETE'])
@customer_required
@login_required
def delete_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    if purchase.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    db.session.delete(purchase)
    try:
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@order.route('/edit_request/<int:request_id>', methods=['POST'])
@login_required
def edit_request(request_id):
    req = Authorization.query.get_or_404(request_id)

    if req.user_id != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    req.client_first_name = request.form.get('client_first_name', req.client_first_name)
    req.client_last_name = request.form.get('client_last_name', req.client_last_name)
    req.client_phone_number = request.form.get('client_phone_number', req.client_phone_number)
    req.client_location = request.form.get('client_location', req.client_location)
    req.lading_bills_identifier = request.form.get('lading_number', req.lading_bills_identifier)
    req.agent_first_name = request.form.get('agent_first_name', req.agent_first_name)
    req.agent_last_name = request.form.get('agent_last_name', req.agent_last_name)
    req.shipping_company_title = request.form.get('shipping_company_title', req.shipping_company_title)

    files = []
    if 'client_signature_url' in request.files:
        files.append(request.files['client_signature_url'])
    if 'client_id_card_url' in request.files:
        files.append(request.files['client_id_card_url'])

    if files:
        saved_files = save_files(files, f"authorization_files/{req.id}")
        req.client_signature_url = saved_files[0] if len(saved_files) > 0 else req.client_signature_url
        req.client_id_card_url = saved_files[1] if len(saved_files) > 1 else req.client_id_card_url

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': _('Demande mise à jour!')}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    

@order.route('/delete_request/<int:request_id>', methods=['DELETE'])
@login_required
def delete_request(request_id):
    req = Authorization.query.get_or_404(request_id)
    if req.user_id != current_user.id:
        return jsonify({"success": False, "message": _("Accès non autorisé")}), 403

    db.session.delete(req)
    db.session.commit()
    return jsonify({"success": True, "message": _("Votre demande a été bien supprimé")})

@order.route('/delete_purchase/<int:purchase_id>', methods=['DELETE'])
@login_required
def delete_client_purchase(purchase_id):
    if not(current_user.is_responsible()):
        abort(403)
    purchase = Purchase.query.get_or_404(purchase_id)
    if purchase is None:
        return jsonify({'message': 'Purchase not found'}), 404

    try:
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({'message':_('Commande supprimée')}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': _('Erreur lors de la suppression'), 'error': str(e)}), 500
    

@order.route('/quote/delete/<int:quote_id>', methods=['DELETE'])
@login_required
def delete_quote(quote_id):
    quote = Authorization.query.get_or_404(quote_id)
    if quote:
        db.session.delete(quote)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': _('Demande Introuvable')}), 404

@order.route('/quote/edit/<int:quote_id>', methods=['PUT'])
@login_required
@customer_required
def edit_quote(quote_id):
    quote = Authorization.query.get_or_404(quote_id)
    if not quote:
        return jsonify({'success': False, 'message': _('Demande Introuvable')}), 404

    data = request.json
    if 'client_first_name' in data:
        quote.client_first_name = data['client_first_name']
    if 'client_last_name' in data:
        quote.client_last_name = data['client_last_name']
    if 'client_phone_number' in data:
        quote.client_phone_number = data['client_phone_number']
    if 'client_email_adress' in data:
        quote.client_email_adress = data['client_email_adress']
    if 'shipping_company_title' in data:
        quote.shipping_company_title = data['shipping_company_title']
    if 'lading_bills_identifier' in data:
        quote.lading_bills_identifier = data['lading_bills_identifier']
    if 'service_fees' in data:
        quote.service_fees = data['service_fees']

    db.session.commit()
    return jsonify({'success': True})


@order.route('/create_new_container_release_letter', methods=['POST'])
@login_required
def create_container_letter():
    try:
        data = request.form
        client_type = data.get("client_type", "person")

        authorization_data = {
            "client_first_name": data.get("client_first_name", ""),
            "client_last_name": data["client_last_name"],
            "client_phone_number": data["client_phone_number"],
            "client_email_address": data.get("client_email_address"),
            "client_location": data["client_location"],
            "agent_first_name": data["agent_first_name"],
            "agent_last_name": data["agent_last_name"],
            "agent_email_address": data.get("agent_email_address"),
            "shipping_company_title": data["shipping_company"],
            "lading_bills_identifier": data["lading_bills_identifier"],
            "company_id": data["company_id"],
            "is_company": client_type == "company"
        }


        if client_type == "company":
            authorization_data.update({
                "company_proof_nif": data.get("company_proof_nif"),
                "company_proof_rccm": data.get("company_proof_rccm"),
                "company_name": data.get("company_name")
            })

        company_authorization_data = {
            "company_email": data.get("company_email_address"),
            "company_phone": data.get("company_phone_number"),
            "company_address": data.get("company_location"),
            "lading_bills_identifier": data["lading_bills_identifier"],
            "agent_first_name": data["agent_first_name"],
            "agent_last_name": data["agent_last_name"],
        }

        authorization = Authorization(**authorization_data)

        db.session.add(authorization)
        db.session.commit()
        
        current_date = datetime.today().strftime("%d/%m/%Y")

        template = "reports/shipping/container_release_letter_company_msc.html" if client_type == "company" else "reports/shipping/container_release_letter_msc.html"

        html_content = render_template(
            template, 
            data=data, 
            date=current_date,
            company_authorization_data=company_authorization_data
        )

        pdf_stream = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_stream)
        pdf_stream.seek(0)

        if client_type == 'company':
            pdf_filename = f"{authorization.company_name}_N°_{authorization.id}.pdf"
        else:
            pdf_filename = f"{authorization.client_first_name}_{authorization.client_last_name}_N°_{authorization.id}.pdf"

        response_data = {
            "success": True,
            "title": f"Demande N°{authorization.id} créee!",
            "message": "La nouvelle demande a bien été créee!",
            "confirmButtonText": "OK",
            "pdf_filename": pdf_filename
        }

        json_data = json.dumps(response_data)
        json_data = json_data.replace('\n', '').replace('\r', '')

        response = make_response(pdf_stream.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={pdf_filename}'
        response.headers['X-JSON-Data'] = json_data
        return response

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@order.route("/prepare_send_container_release_letter/<int:quote_id>/<int:company_id>", methods=["GET", "POST"])
def prepare_send_container_release_letter(quote_id, company_id):
    company = Company.query.get_or_404(company_id)
    quote = Authorization.query.get_or_404(quote_id)
    if request.method == "POST":
        client_name = request.form.get("client_name")
        agent_name = request.form.get("agent_name")
        subject = request.form.get("subject")
        message = request.form.get("message")

        flash("Email prepared successfully!", "success")
        return redirect(url_for("prepare_send_container_release_letter", quote_id=quote_id))

    return render_template(
        "dashboard/@support_team/shipping/prepare_container_release_email.html", 
        quote=quote,
        company=company
    )


@order.route('/search-authorizations/<int:company_id>', methods=['GET'])
def search_authorizations(company_id):
    term = request.args.get('term', '').strip()
    field = request.args.get('field', '').strip()
    
    if not term or not field:
        return jsonify([])
    
    allowed_fields = {
        'client_last_name', 'client_first_name', 'client_location',
        'client_phone_number',
        'agent_last_name', 'agent_first_name',
        'company_proof_nif', 'company_proof_rccm',
        'company_name'
    }
    
    if field not in allowed_fields:
        return jsonify([])
    
    try:
        filter_condition = and_(
            getattr(Authorization, field).ilike(f'%{term}%'),
            Authorization.company_id == company_id
        )
        
        result = Authorization.query.filter(filter_condition).first()
        
        if not result:
            return jsonify([])
            
        auth_data = {
            'client_last_name': result.client_last_name,
            'client_first_name': result.client_first_name,
            'client_location': result.client_location,
            'client_phone_number': result.client_phone_number,
            'client_phone_number_display': f"{result.client_phone_number} - {result.client_last_name}",
            'agent_last_name': result.agent_last_name,
            'agent_first_name': result.agent_first_name,
            'company_proof_nif': result.company_proof_nif,
            'company_proof_nif_display': f"{result.company_proof_nif} - {result.company_name}",
            'company_proof_rccm': result.company_proof_rccm,
            'company_proof_rccm_display': f"{result.company_proof_rccm} - {result.company_name}",
            'company_name': result.company_name
        }
        return jsonify([auth_data])
            
    except Exception as e:
        return jsonify([])