import os
from dotenv import load_dotenv

load_dotenv()

def get_database_path(database_name="app.db"):
    """
    Generate a writable path for the database file based on the OS.
    The database will be stored in the 'Documents/Ressync folder inside the user's home directory.
    """
    home_dir = os.path.expanduser("~")

    documents_dir = os.path.join(home_dir, "Documents", "Ressync")

    os.makedirs(documents_dir, exist_ok=True)

    return os.path.join(documents_dir, database_name)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    RESSYNC_CEO = os.environ.get('RESSYNC_CEO')
    RESSYNC_HR_MANAGER = os.environ.get('RESSYNC_HR_MANAGER')
    RESSYNC_ACCOUNTANT = os.environ.get('RESSYNC_ACCOUNTANT')
    RESSYNC_SALES_DIRECTOR = os.environ.get('RESSYNC_SALES_DIRECTOR')
    RESSYNC_AGENTS_EMAILS = os.environ.get('RESSYNC_AGENTS_EMAILS')
    BABEL_DEFAULT_LOCALE = 'fr'
    BABEL_SUPPORTED_LOCALES = ['en', 'fr', 'de', 'zh', 'ru', 'tr']
    BABEL_TRANSLATION_DIRECTORIES = './translations'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{get_database_path('app.db')}"
    PLACEHOLDER_STATIC_URL = os.environ.get('PLACEHOLDER_PRODUCTION_STATIC_URL')
    LOGIN_URL = os.environ.get('PRODUCTION_LOGIN_URL')
    SERVER_URL = os.environ.get('PRODUCTION_SERVER_URL')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{get_database_path('app.db')}"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URL')
    PLACEHOLDER_STATIC_URL = os.environ.get('PLACEHOLDER_PRODUCTION_STATIC_URL')
    LOGIN_URL = os.environ.get('PRODUCTION_LOGIN_URL')
    SERVER_URL = os.environ.get('PRODUCTION_SERVER_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}