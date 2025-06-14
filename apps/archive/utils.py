import random, string
import os
import qrcode
from flask import jsonify
from werkzeug.utils import secure_filename
from firebase_admin import storage, initialize_app, credentials
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import platform
from pathlib import Path
import requests
from urllib.parse import urlparse

load_dotenv()

firebase_config = {
    "type": os.getenv('FIREBASE_TYPE'),
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
    "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
}

cred = credentials.Certificate(firebase_config)
default_app = initialize_app(cred, {'storageBucket': 'afrilog-797e8.appspot.com'})

def save_files(files, folder):
    saved_files = []
    bucket = storage.bucket()

    for file in files:
        if file:
            filename = secure_filename(file.filename)
            blob = bucket.blob(f"{folder}/{filename}")
            blob.upload_from_file(file)
            blob.make_public()
            saved_files.append(blob.public_url)

    return saved_files

def save_product_pictures(files):
    return save_files(files, "product_pictures")

def save_shop_product_barcodes(files):
    return save_files(files, "shop_product_barcodes")

def save_docs(files):
    return save_files(files, "documents")

def save_message_file(file):
    bucket = storage.bucket()
    filename = secure_filename(file.filename)
    blob = bucket.blob(f"messages/{filename}")
    blob.upload_from_file(file)
    blob.make_public()
    return blob.public_url

def generate_qr_code(token):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    qr_image = BytesIO()
    img.save(qr_image, 'PNG')
    qr_image.seek(0)

    filename = f"qr_codes/{token}.png"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_file(qr_image, content_type='image/png')
    blob.make_public()

    return blob.public_url

def generate_barcode(token):
    code128 = barcode.get_barcode_class('code128')
    barcode_instance = code128(str(token), writer=ImageWriter())
    buffer = BytesIO()
    barcode_instance.write(buffer)
    buffer.seek(0)
    filename = f"barcodes/{token}.png"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_file(buffer, content_type='image/png')
    blob.make_public()

    return blob.public_url

def save_file_locally(url, save_directory=None):
    try:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if save_directory is None:
            system = platform.system()
            if system == 'Windows':
                save_directory = os.path.join(str(Path.home()), 'Downloads')
            elif system == 'Linux':
                save_directory = os.path.join(str(Path.home()), 'Downloads')
            elif system == 'Darwin':
                save_directory = os.path.join(str(Path.home()), 'Downloads')
            else:
                save_directory = os.path.join(str(Path.home()), 'Downloads')
        
        os.makedirs(save_directory, exist_ok=True)
        
        response = requests.get(url)
        if response.status_code == 200:
            local_file_path = os.path.join(save_directory, filename)
            with open(local_file_path, 'wb') as f:
                f.write(response.content)
            return local_file_path
        else:
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(16))
    return password

def get_tasks_for_user(user_email):
    from ..models.general.task import Task
    from ..models.general.user import User

    user = User.query.filter_by(email=user_email).first()
    if user:
        tasks = Task.query.filter_by(assigned_to=user.id).all()
    else:
        tasks = []

    return tasks