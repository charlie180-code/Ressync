from flask import Blueprint

career = Blueprint('career', __name__)

from . import controllers
