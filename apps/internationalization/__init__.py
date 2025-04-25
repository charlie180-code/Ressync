from flask import Blueprint

internationalization = Blueprint('internationalization', __name__)

from . import controllers
