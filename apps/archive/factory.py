from flask import Flask
from flask_cors import CORS 
from config import config
from .. import db

def create_app(config_name='development'):
    cloudsquish = Flask(__name__, static_folder='static')
    cloudsquish.config.from_object(config['development'])
    config['development'].init_app(cloudsquish)
    db.init_app(cloudsquish)
    from . import archive as archive_blueprint
    cloudsquish.register_blueprint(archive_blueprint, url_prefix='/archive/v1')
    CORS(cloudsquish)
    return cloudsquish
