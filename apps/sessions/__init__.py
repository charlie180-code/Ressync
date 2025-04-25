from flask import Blueprint

session = Blueprint('session', __name__)

from . import controllers
