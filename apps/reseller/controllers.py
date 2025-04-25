from flask import render_template, request, jsonify, redirect, url_for, abort
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from . import reseller
from ..decorators import consultant_required
from ..models.shipping.product import Product
from ..models.shipping.store import Store
from ..models.general.user import User
from ..models.general.role import Role
from ..models.general.company import Company
from ..utils import save_files, generate_barcode, generate_password, save_file_locally
from .. import db
from .emails.welcome import welcome_reseller
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from barcode import EAN13
from dotenv import load_dotenv
from flask_babel import gettext as _

load_dotenv()

@reseller.route("/products", methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@consultant_required
def products():
    if request.method == 'POST':
        title = request.form.get('title')
        cost = float(request.form.get('cost'))
        stock = int(request.form.get('stock', 0))
        category = request.form.get('category')
        provider = request.form.get('provider')
        provider_location = request.form.get('provider_location')
        publish = 'publish' in request.form
        image_file = request.files.get('product_img_url')

        if not category:
            return jsonify(
                {
                    "success": False, 
                    "title": _('Error!'),
                    "message": _('Catégorie du produit est requise'),
                    "confirmButtonText": _('OK')
                }
            ), 400

        if image_file:
            image_urls = save_files([image_file], "shop_product_images")
            product_img_url = image_urls[0] if image_urls else None
        else:
            product_img_url = None

        new_product = Product(
            title=title,
            cost=cost,
            stock=stock,
            category=category,
            provider=provider,
            provider_location=provider_location,
            product_img_url=product_img_url,
            publish=publish,
            user_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()

        barcode_url = generate_barcode(new_product.id)
        new_product.barcode_url = barcode_url
        db.session.commit()

        return redirect(url_for('main.products'))

    elif request.method == 'PUT':
        product_id = request.form.get('id')
        product = Product.query.get_or_404(product_id)

        title = request.form.get('title')
        cost = float(request.form.get('cost'))
        stock = int(request.form.get('stock', 0))
        category = request.form.get('category')
        publish = 'publish' in request.form
        product_img = request.files.get('product_img_url')


        if product_img:
            product_img_url = save_files([product_img], 'shop_product_images')[0]
        else:
            product_img_url = product.product_img_url

        product.title = title
        product.cost = cost
        product.stock = stock
        product.category = category
        product.product_img_url = product_img_url
        product.publish = publish

        db.session.commit()

        barcode_url = generate_barcode(product.id)
        product.barcode_url = barcode_url
        db.session.commit()

        return jsonify(
            {
                "title": _('Mise à jour effectuée'),
                "message": _('Le produit a bien été mis à jour'),
                "confirmButtonText": _("OK"),
                "success": True
            }
        ), 200

    elif request.method == 'DELETE':
        product_id = request.form.get('id')
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()

        return jsonify(
            {
                "title": _('Supprimé'),
                "message": _('Produit supprimé'),
                "success": True
            }
        ), 200

    else:
        products = Product.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard/@support_team/products.html', products=products)
    


@reseller.route('/stores/<int:company_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def stores(company_id):
    company = Company.query.get_or_404(company_id)
    if not(current_user.is_responsible() or current_user.is_sales()):
        abort(403)
    if request.method == 'GET':
        stores = Store.query.filter_by(company_id=company.id).all()
        return render_template('dashboard/@support_team/stores.html', stores=stores, company=company)

    elif request.method == 'POST':
        data = request.form
        logo_files = request.files.getlist('logo')
        logo_urls = save_files(logo_files, 'store_logos')
        logo_url = logo_urls[0] if logo_urls else None

        password = generate_password()
        hashed_password = generate_password_hash(password)

        new_user = User(
            email=data['email'],
            password_hash=hashed_password,
        )

        db.session.add(new_user)
        db.session.commit()

        stored_user = User.query.filter_by(email=data['email']).first()

        if stored_user:
            reseller_role = Role.query.filter_by(name='Reseller').first()
            stored_user.role_id = reseller_role.id
            db.session.commit() 

        store = Store(
            name=data['name'],
            location=data['location'],
            email=data['email'],
            phone=data.get('phone'),
            logo_file_url=logo_url,
            company_id=company.id
        )

        db.session.add(store)
        db.session.commit()

        welcome_reseller(new_user.email, password)

        return jsonify(message= _("Le magasin a bien été ajouté."), title= _("Magasin ajouté!")), 201

    elif request.method == 'PUT':
        try:
            store_id = request.form['id']
            store = Store.query.get_or_404(store_id)
            
            store.name = request.form['name']
            store.location = request.form['location']
            store.phone = request.form.get('phone')

            new_email = request.form['email']
            if store.email != new_email:
                store.email = new_email
                
                user = User.query.filter_by(email=store.email).first()
                if user:
                    user.email = new_email
                    db.session.add(user)

            logo_files = request.files.getlist('logo')
            if logo_files:
                logo_urls = save_files(logo_files, 'store_logos')
                store.logo_file_url = logo_urls[0] if logo_urls else store.logo_file_url

            db.session.commit()
            return jsonify(message= _("Les infos du magasin ont bien été mis à jour"), title= _("Infos mises à jour!"))

        except Exception as e:
            db.session.rollback()
            return jsonify(error=str(e)), 400

    elif request.method == 'DELETE':
        store_id = request.form['id']
        store = Store.query.get_or_404(store_id)
        store_email = store.email
        store_repr = User.query.filter_by(email=store_email).first()

        if store_repr:
            db.session.delete(store_repr)
            
        db.session.delete(store)
        db.session.commit()
        return jsonify(message= _("Le magasin a bien été retiré"), title= _("Supprimé"))
    

@reseller.route('/get-store_details/<int:store_id>', methods=['GET'])
@login_required
def get_store(store_id):
    if not(current_user.is_responsible()):
        abort(403)
    store = Store.query.get_or_404(store_id)
    return jsonify({
        'id': store.id,
        'name': store.name,
        'location': store.location,
        'email': store.email,
        'logo_file_url': store.logo_file_url,
        'phone': store.phone
    })


@reseller.route("/download_barcode/<int:product_id>", methods=['GET'])
@login_required
@consultant_required
def download_barcode(product_id):
    product = Product.query.get_or_404(product_id)

    token = f"{product.title}-{product.id}"
    barcode_url = generate_barcode(token)

    local_file_path = save_file_locally(barcode_url)

    if local_file_path:
        try:
            pdf_buffer = BytesIO()

            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            c.drawString(100, 750, f"Product Title: {product.title}")
            c.drawString(100, 730, f"Token: {token}")

            if local_file_path.endswith('.png'):
                img = ImageReader(local_file_path)
                c.drawImage(img, 100, 600, width=200, height=100)

            c.save()

            pdf_buffer.seek(0)

            return send_file(pdf_buffer, as_attachment=True, download_name=f"{product.title}_{token}.pdf")

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return jsonify({"success": False, "message": "Failed to generate PDF"}), 500

    else:
        return jsonify({"success": False, "message": "Failed to download the barcode"}), 500