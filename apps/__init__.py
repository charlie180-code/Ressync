from flask import Flask, session, request, redirect, g, render_template, jsonify
import requests
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_oauthlib.client import OAuth
from flask_restcountries import CountriesAPI
from flask_migrate import Migrate
from flask_babel import Babel
from .filters import mask_token
from .utils import get_tasks_for_user
from datetime import datetime
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from sqlalchemy import text
import sys
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
moment = Moment()
oauth = OAuth()
rapi = CountriesAPI()
migrate = Migrate()
babel = Babel()


def create_app(development=True, template_folder='templates', static_folder='static'):
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(config['development'])
    config['development'].init_app(app)
    app.config['JSON_AS_ASCII'] = False
    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    rapi.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .sessions import session as session_blueprint
    app.register_blueprint(session_blueprint, url_prefix='/sessions/v1')

    from .classroom import classroom as classroom_blueprint
    app.register_blueprint(classroom_blueprint, url_prefix='/classrooms/v1')

    from .section import section as section_blueprint
    app.register_blueprint(section_blueprint, url_prefix='/sections/v1')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .promotion import promote as promote_blueprint
    app.register_blueprint(promote_blueprint, url_prefix='/promote/v1')

    from .note import note as note_blueprint
    app.register_blueprint(note_blueprint, url_prefix='/note/v1')

    from .insights import insights as insight_blueprint
    app.register_blueprint(insight_blueprint, url_prefix='/insights/v1')

    from .msg import msg as msg_blueprint
    app.register_blueprint(msg_blueprint, url_prefix='/msg/v1')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .wallet import wallet as wallet_blueprint
    app.register_blueprint(wallet_blueprint, url_prefix='/wallet/v1')

    from .task import task as task_blueprint
    app.register_blueprint(task_blueprint, url_prefix='/task/v1')

    from .archive import archive as archive_blueprint
    app.register_blueprint(archive_blueprint, url_prefix='/archive/v1')

    from .blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint)

    from .calendar import calendar as calendar_blueprint
    app.register_blueprint(calendar_blueprint, url_prefix='/calendar/v1')

    from .ads import advertise as ads_blueprint
    app.register_blueprint(ads_blueprint, url_prefix='/ads/v1')

    from .reseller import reseller as reseller_blueprint
    app.register_blueprint(reseller_blueprint)

    from .ordering import order as order_blueprint
    app.register_blueprint(order_blueprint, url_prefix='/order/v1')

    from .accounting import accounting as accounting_blueprint
    app.register_blueprint(accounting_blueprint, url_prefix='/accounting/v1')

    from .career import career as career_blueprint
    app.register_blueprint(career_blueprint, url_prefix='/career/v1')

    from .internationalization import internationalization as internationalization_blueprint
    app.register_blueprint(internationalization_blueprint, url_prefix='/i18n/v1')

    def get_locale():
        user = getattr(g, 'user', None)
        if user and user.locale in app.config['BABEL_SUPPORTED_LOCALES']:
            return user.locale
        return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

    def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone

    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)

    @app.context_processor
    def inject_get_locale():
        return {'get_locale': get_locale}

    @app.context_processor
    def inject_get_company_files():
        from apps.auth.utils import get_company_files
        return {'get_company_files': get_company_files}

    @app.route('/set_language', methods=['POST'])
    def set_language():
        language = request.form['language']
        response = redirect(request.referrer)
        response.set_cookie('language', language)
        return response

    @app.template_filter
    def _jinja2_filter_truncate(s, length=17):
        if len(s) > length:
            return s[:length] + '...'
        return s

    filters.register_filters(app)

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.utcnow().year}

    def check_internet_connection():
        url = "https://www.google.com"
        timeout = 8
        try:
            response = requests.get(url, timeout=timeout)
            return True if response.status_code == 200 else False
        except requests.ConnectionError:
            return False

    @app.context_processor
    def inject_internet_status():
        return {'is_connected': check_internet_connection()}

    from .models.utils import roles_translations

    @app.context_processor
    def inject_roles_translations():
        return dict(roles_translations=roles_translations)

    @app.context_processor
    def inject_tasks():
        user_email = session.get('email')
        if user_email:
            tasks = get_tasks_for_user(user_email)
        else:
            tasks = []
        return dict(tasks=tasks)


    @app.template_filter('strftime')
    def _jinja2_filter_strftime(dt, fmt=None):
        if dt:
            return dt.strftime(fmt)
        else:
            return None

    with app.app_context():
        from .models.general.role import Role
        db.create_all()
        Role.insert_roles()

    @app.errorhandler(404)
    def page_not_found(e):
        company_id = session.get('company_id')
        from apps.models.general.company import Company
        company = Company.query.get(company_id) if company_id else None
        return render_template('errors/404.html', company=company)

    @app.errorhandler(403)
    def forbidden(e):
        company_id = session.get('company_id')
        from apps.models.general.company import Company
        company = Company.query.get(company_id) if company_id else None
        return render_template('errors/403.html', company=company)

    @app.errorhandler(500)
    def internal_server_error(e):
        company_id = session.get('company_id')
        from apps.models.general.company import Company
        company = Company.query.get(company_id) if company_id else None
        return render_template('errors/500.html', company=company)

    @app.errorhandler(400)
    def bad_request(e):
        company_id = session.get('company_id')
        from apps.models.general.company import Company
        company = Company.query.get(company_id) if company_id else None
        return render_template('errors/400.html', company=company)


    @app.route('/health')
    def health_check():
        return jsonify(
            {'Message' :'Hello from Ressync Team, Server is good and you\'re ready to go'},
            200
        )

    CORS(app)
    
    return(app)