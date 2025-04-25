# app/api/factory.py
from flask import Flask
from config import config
from .. import db

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)

    from . import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/msg/v1')

    return app
