import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl
import os
import base64
import json
from werkzeug.utils import secure_filename
from flask import render_template, jsonify, request, current_app, url_for
from flask_login import login_required, current_user
from ..models.general.contact import Contact
from ..models.general.subscriber import Subscriber
from ..models.general.company import Company
from ..models.general.user import User
import os
from flask_mail import Message
from .. import mail, db
from twilio.rest import Client
from . import msg
from flask_babel import gettext as _
from ..auth.utils import check_internet_connection, save_file_locally
from ..utils import save_files
from ..user.utils import fetch_emails


@msg.route('/contacts/<int:company_id>')
@login_required
def view_contacts(company_id):
    company = Company.query.get_or_404(company_id)
    page = request.args.get('page', 1, type=int)
    contacts = Contact.query.filter_by(company_id=company.id, user_id=current_user.id)\
                  .order_by(Contact.id.desc())\
                  .paginate(page=page, per_page=10)
    return render_template('dashboard/customers/view_contacts.html', company=company, contacts=contacts)

@msg.route('/messages/recent/<int:company_id>', methods=['GET'])
@login_required
def recent_messages(company_id):
    recent_messages = (
        Message.query
        .filter_by(receiver_id=current_user.id, company_id=company_id)
        .order_by(Message.timestamp.desc())
        .limit(10)
        .all()
    )

    return render_template('messages/recent_messages.html', recent_messages=recent_messages)


@msg.route('/messages/programmed', methods=['GET'])
def programmed_messages():
    # Fetch programmed messages from the database or other source
    programmed_messages = []

    # Example: fetching programmed messages from a database
    # programmed_messages = Message.query.filter_by(status='programmed').all()

    return render_template('messages/programmed_messages.html', programmed_messages=programmed_messages)


@msg.route("/mailbox/new_message/<int:company_id>", methods=['GET', 'POST', 'DELETE'])
@login_required
def new_message(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        data = request.get_json()
        sender_email = data.get('email')
        receiver_email = data.get('receiver')
        message_body = data.get('message')

        sender = User.query.filter_by(email=sender_email).first()
        receiver = User.query.filter_by(email=receiver_email).first()

        if not sender or not receiver:
            return jsonify({'message': 'Expéditeur ou récepteur invalide'}), 400

        new_message = Message(
            body=message_body,
            sender_id=sender.id,
            receiver_id=receiver.id
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({'message': 'Message envoyé avec succès!'}), 200  

    return render_template('api/messages/new_message.html', company=company)


@msg.route('/send-message/<int:company_id>', methods=['POST'])
def send_email(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.form

    first_name = data.get('first-name')
    last_name = data.get('last-name')
    company = data.get('company', '')
    email = data.get('email')
    phone = data.get('author_phone_number_raw')
    message_content = data.get('message')

    subject = "Soumission de formulaire de contact pour les ventes"
    sender = ("Site web AfriLog", 'noreply@afrilog.net')
    recipients = [os.environ.get('COMPANY_SALES_MANAGER')]

    body = f"""
    Vous avez une nouvelle soumission de formulaire de contact.

    Nom : {first_name} {last_name}
    Entreprise : {company}
    Email : {email}
    Téléphone : {phone}

    Message :
    {message_content}
    """

    body = body.format(first_name=first_name, last_name=last_name, company=company, email=email, phone=phone, message_content=message_content)

    try:
        msg = Message(subject, sender=sender, recipients=recipients, body=body)
        mail.send(msg)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))
    


@msg.route('/send-whatsapp-message/<int:company_id>', methods=['POST'])
def send_whatsapp_message(company_id):
    company = Company.query.get_or_404(company_id)
    account_sid = os.environ.get('TWILIO_ACCOUNT_ID_SECRET')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = 'whatsapp:+14155238886'

    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    message_text = data.get('message')
    phone_number = data.get('phone')

    if not phone_number:
        return jsonify({'error': 'Phone number is required'}), 400

    body = f"Nom du client: {first_name}, Prénom du client: {last_name}, Message: {message_text}"

    try:

        existing_contact = Contact.query.filter_by(phone=phone_number).first()
        
        if existing_contact:
            pass
        
        else:
            new_contact = Contact(
                first_name=first_name,
                last_name=last_name,
                phone=phone_number,
                message=message_text
            )

            db.session.add(new_contact)
            db.session.commit()

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=body,
            from_=twilio_phone_number,
            to=f'whatsapp:{phone_number}'
        )

        print(message.sid)

        return jsonify({'message': 'Message sent successfully'}), 200

    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        return jsonify({'error': 'Failed to send message'}), 500
    

@msg.route('/store_a_subscriber/<int:company_id>', methods=['POST'])
def subscriber_saver(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.json 
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    existing_subscriber = Subscriber.query.filter_by(email=email).first()
    
    if existing_subscriber:
        return jsonify({'error': 'Contact already exists in the database'}), 400
    
    new_subscriber = Subscriber(email=email, company_id=company.id)
    
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return jsonify({'message': 'New contact successfully added in the database'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add contact: {str(e)}'}), 500
    finally:
        db.session.close()


@msg.route('/create_contact/<int:company_id>', methods=['GET', 'POST'])
@login_required
def create_contact(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        gender = data.get('gender')
        source = _('Réperoire personnel')
        message = ' '

        # check if the phone number exists
        existing_phone = Contact.query.filter_by(phone=phone, user_id=current_user.id).first()

        if existing_phone:
            return jsonify({'success': False, 'errorType': 'DuplicatePhone'}), 401
        
        # check if the email exists
        existing_email = Contact.query.filter_by(email=email, user_id=current_user.id).first()

        if existing_email:
            return jsonify({'success': False, 'errorType': 'DuplicateEmail'}), 401
        
    
        new_contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            gender=gender,
            company_id=company.id,
            source=source,
            message=message,
            user_id=current_user.id
        )

        try:
            db.session.add(new_contact)
            db.session.commit()
            return jsonify({'title' : _('Contact Ajouté'), 'message': _('Contact ajouté avec succès')}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    return render_template('api/customers/contacts/create_contact.html', company=company)


@msg.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'email': contact.email,
            'phone': contact.phone,
            'gender': contact.gender
        })
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        if not data.get('first_name') or not data.get('last_name'):
            return jsonify({'success': False, 'message': _('Les nom et prénom sont requis')}), 400
        
        # Check for duplicate email (if changed)
        if data.get('email') and data['email'] != contact.email:
            existing_email = Contact.query.filter(
                Contact.email == data['email'],
                Contact.user_id == current_user.id,
                Contact.id != contact.id
            ).first()
            if existing_email:
                return jsonify({'success': False, 'message': _('Cette addresse existe déja')}), 409
        
        # Check for duplicate phone (if changed and provided)
        if data.get('phone') and data['phone'] != contact.phone:
            existing_phone = Contact.query.filter(
                Contact.phone == data['phone'],
                Contact.user_id == current_user.id,
                Contact.id != contact.id
            ).first()
            if existing_phone:
                return jsonify({'success': False, 'message': _('Le numéro existe déja')}), 409
        
        try:
            contact.first_name = data.get('first_name')
            contact.last_name = data.get('last_name')
            contact.email = data.get('email')
            contact.phone = data.get('phone')
            contact.gender = data.get('gender')
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': _('Contact mis à jour'),
                'title': _('Effectué')
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500


@msg.route('/delete_contact/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    
    if contact.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': _('Suppression effectuée'),
            'title': _('Supprimé')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500



@msg.route('/get-contacts/<int:company_id>')
@login_required
def get_contacts(company_id):
    company = Company.query.get_or_404(company_id)
    contacts = Contact.query.filter_by(company_id=company.id).all()
    contacts_data = [{
        'id': contact.id,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone': contact.phone
    } for contact in contacts]
    return jsonify(contacts_data)


@msg.route('/test_email_connection', methods=['POST'])
@login_required
def test_email_connection():
    try:
        email_provider = request.form.get('email_provider', 'gmail')
        email_username = request.form.get('email_username')
        email_password = request.form.get('email_password')
        smtp_server = request.form.get('smtp_server')
        smtp_port = request.form.get('smtp_port', 587, type=int)

        if not email_username or not email_password:
            return jsonify({'success': False, 'message': 'Email credentials are required'}), 400

        if email_provider == 'custom' and not smtp_server:
            return jsonify({'success': False, 'message': 'SMTP server is required for custom provider'}), 400

        smtp_servers = {
            'gmail': ('smtp.gmail.com', 587),
            'outlook': ('smtp.office365.com', 587),
            'yahoo': ('smtp.mail.yahoo.com', 587),
            'icloud': ('smtp.mail.me.com', 587),
            'custom': (smtp_server, smtp_port)
        }

        smtp_host, smtp_port = smtp_servers.get(email_provider, ('smtp.gmail.com', 587))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(email_username, email_password)

        return jsonify({'success': True, 'message': 'Connection successful'})

    except smtplib.SMTPAuthenticationError:
        return jsonify({'success': False, 'message': 'Authentication failed - wrong username or password'}), 401
    except smtplib.SMTPException as e:
        return jsonify({'success': False, 'message': f'SMTP error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'}), 500


@msg.route('/send_authorization_email', methods=['POST'])
@login_required
def send_authorization_email():
    try:
        def parse_json_field(field_name, default=None):
            try:
                data = request.form.get(field_name)
                return json.loads(data) if data else default
            except json.JSONDecodeError:
                current_app.logger.error(f"Invalid JSON in {field_name} field")
                return default

        to_emails = parse_json_field('to', [])
        subject = request.form.get('subject', '').strip()
        html_message = request.form.get('message', '').strip()
        attachments = parse_json_field('attachments', [])
        cc_emails = parse_json_field('cc', [])

        if not to_emails:
            return jsonify({
                'success': False,
                'title': _('Erreur de validation'),
                'message': _('Au moins un destinataire est requis')
            }), 400

        if not subject:
            return jsonify({
                'success': False,
                'title': _('Erreur de validation'),
                'message': _('Le sujet est requis')
            }), 400

        if not html_message or html_message in ['<p><br></p>', '<p></p>']:
            return jsonify({
                'success': False,
                'title': _('Erreur de validation'),
                'message': _('Le message est requis')
            }), 400

        def is_valid_email(email):
            return '@' in email and '.' in email.split('@')[-1]

        invalid_emails = [email for email in to_emails + cc_emails if not is_valid_email(email)]
        if invalid_emails:
            return jsonify({
                'success': False,
                'title': _('Erreur de validation'),
                'message': f"Adresses email invalides: {', '.join(invalid_emails)}"
            }), 400

        if not all([current_user.email_username, current_user.email_password]):
            return jsonify({
                'success': False,
                'title': _('Configuration manquante'),
                'message': _('Les identifiants email ne sont pas configurés')
            }), 400

        company_logo_url = current_user.company.logo_url if current_user.company else ''
        company_title = current_user.company.title if current_user.company else ''

        # Build the signature HTML
        signature_html = f"""
        <table style="border-collapse: collapse; margin-top: 20px;">
            <tr><td style="padding: 2px 0;">{(current_user.signature_word or 'Kind Regards') + ','}</td></tr>
            <tr><td style="padding: 2px 0;"><strong>{current_user.signature_name or ''}</strong></td></tr>
            <tr><td style="padding: 2px 0;">{current_user.signature_title or ''}</td></tr>
            <tr><td style="padding: 2px 0;">{current_user.signature_phone or ''}</td></tr>
            <tr><td style="padding: 2px 0;">{company_title}</td></tr>
            <tr><td style="padding: 2px 0;">
                <img src="{company_logo_url or ''}" alt="Company Logo" style="height: 50px; margin-right: 10px;">
                <img src="{current_user.signature_additional_badge or ''}" alt="Company Badge" style="height: 50px;">
            </td></tr>
        </table>
        """

        # Combine message and signature
        full_html = f"""
        <div>
            {html_message}
            {signature_html}
        </div>
        """

        msg = MIMEMultipart()
        msg['From'] = current_user.email_username
        msg['To'] = ', '.join(to_emails)
        msg['Cc'] = ', '.join(cc_emails) if cc_emails else ''
        msg['Subject'] = subject
        msg.attach(MIMEText(full_html, 'html'))

        for attachment in attachments:
            try:
                if not all(key in attachment for key in ['name', 'data']):
                    continue

                part = MIMEBase('application', 'octet-stream')
                part.set_payload(base64.b64decode(attachment['data']))
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={secure_filename(attachment["name"])}'
                )
                msg.attach(part)
            except Exception as e:
                current_app.logger.error(f"Failed to process attachment: {str(e)}")
                continue

        smtp_config = {
            'gmail': ('smtp.gmail.com', 587),
            'outlook': ('smtp.office365.com', 587),
            'yahoo': ('smtp.mail.yahoo.com', 587),
            'icloud': ('smtp.mail.me.com', 587),
        }.get(current_user.email_provider or 'gmail', 
            (current_user.smtp_server, current_user.smtp_port or 587))

        try:
            with smtplib.SMTP(smtp_config[0], smtp_config[1]) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(current_user.email_username, current_user.email_password)
                server.send_message(msg)
                
                current_app.logger.info(
                    f"Email sent successfully to {to_emails} "
                    f"(CC: {cc_emails}) with subject: {subject}"
                )

                return jsonify({
                    'success': True,
                    'title': _('Envoyé'),
                    'message': _('Message envoyé'),
                    'redirect_url': url_for('order.new_quotes', company_id=current_user.company_id)
                })

        except smtplib.SMTPAuthenticationError:
            current_app.logger.error("SMTP authentication failed")
            return jsonify({
                'success': False,
                'title': _('Erreur d\'authentification'),
                'message': _('Échec de l\'authentification SMTP')
            }), 401

        except smtplib.SMTPException as e:
            current_app.logger.error(f"SMTP error: {str(e)}")
            return jsonify({
                'success': False,
                'title': _('Erreur SMTP'),
                'message': f"Erreur lors de l'envoi: {str(e)}"
            }), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in send_authorization_email: {str(e)}")
        return jsonify({
            'success': False,
            'title': _('Erreur inattendue'),
            'message': _('Une erreur inattendue est survenue')
        }), 500
    
@msg.route('/email-signature/<int:user_id>', methods=['GET', 'POST'])
@login_required
def email_signature(user_id):
    if request.method == 'POST':
        try:
            user = User.query.get_or_404(current_user.id)
            
            user.signature_name = request.form.get('name', '')
            user.signature_title = request.form.get('title', '')
            user.signature_phone = request.form.get('phone', '')
            user.signature_word = request.form.get('word', '')
            
            if 'badges' in request.files:
                badge_files = request.files.getlist('badges')
                existing_badges = user.signature_additional_badge.split(',') if user.signature_additional_badge else []
                new_badges = []
                
                for badge_file in badge_files:
                    if badge_file.filename != '':
                        if not badge_file.mimetype.startswith('image/'):
                            continue  # Skip non-image files
                        if badge_file.content_length > 2 * 1024 * 1024:
                            continue  # Skip files larger than 2MB
                        
                        try:
                            if check_internet_connection():
                                saved_badge_url = save_files([badge_file], "email_signatures/badges/")[0]
                            else:
                                badge_filename = save_file_locally(badge_file, folder_name="static/email_signatures/badges")
                                saved_badge_url = url_for('static', filename=f"email_signatures/badges/{badge_filename}", _external=True)
                            
                            new_badges.append(saved_badge_url)
                        except Exception as e:
                            continue  # Skip files that fail to save
                
                # Combine existing badges with new ones (remove duplicates if needed)
                all_badges = list(set(existing_badges + new_badges))
                user.signature_additional_badge = ','.join(all_badges) if all_badges else None
            
            db.session.commit()
            return jsonify({
                'success': True,
                'title': _('Effectuée'),
                'message': _('La signature a été bien modifiée'),
                'badges': user.signature_additional_badge.split(',') if user.signature_additional_badge else []
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    user = User.query.get_or_404(current_user.id)
    company = Company.query.get_or_404(current_user.company_id)
    
    badges = user.signature_additional_badge.split(',') if user.signature_additional_badge else []

    
    return render_template('dashboard/@support_team/email_signature.html', 
        user=user, 
        company=company,
        badges=badges
    )



@msg.route("/send_reply", methods=["POST"])
@login_required
def send_reply():
    try:
        to_email = request.form.get("to")
        subject = request.form.get("subject")
        body = request.form.get("replyBody")
        
        smtp_server = current_user.smtp_server or f"smtp.{current_user.email_provider}.com"
        smtp_port = current_user.smtp_port or 587
        email_username = current_user.email_username or current_user.email
        email_password = current_user.email_password
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_username
        msg["To"] = to_email
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_username, email_password)
            server.send_message(msg)
        
        return jsonify({"success": True})
    
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    

@msg.route("/get_emails")
@login_required
def get_emails():
    emails = fetch_emails(current_user)
    return jsonify(emails)