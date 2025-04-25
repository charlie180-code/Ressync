from flask import Blueprint

section = Blueprint('section', __name__)

from . import controllers
